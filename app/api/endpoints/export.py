"""Export endpoint for bulk downloading articles in CSV or JSON format."""

import csv
import io
import json
from datetime import datetime
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article

router = APIRouter(prefix="/export", tags=["export"])


def article_to_dict(article: Article) -> dict:
    """Convert an Article SQLAlchemy model instance to a serializable dict.

    Args:
        article: The Article model instance to convert.

    Returns:
        A dictionary with all article fields, with datetime values converted
        to ISO format strings.
    """
    result = {}
    for column in Article.__table__.columns:
        value = getattr(article, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result


def generate_csv(articles: list[Article]) -> Generator[str, None, None]:
    """Generate CSV content row by row for streaming.

    Args:
        articles: List of Article model instances to serialize.

    Yields:
        CSV rows as strings, starting with the header row.
    """
    columns = [column.name for column in Article.__table__.columns]

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # Write header
    writer.writerow(columns)
    yield buffer.getvalue()
    buffer.seek(0)
    buffer.truncate(0)

    # Write data rows
    for article in articles:
        row = []
        for col in columns:
            value = getattr(article, col)
            if isinstance(value, datetime):
                value = value.isoformat()
            row.append(value)
        writer.writerow(row)
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)


@router.get("/articles", summary="Export all articles as CSV or JSON")
def export_articles(
    format: str = "csv",
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Export all articles in the requested format (CSV or JSON).

    Args:
        format: The export format, either 'csv' or 'json'.
        db: The database session (injected via dependency).

    Returns:
        A StreamingResponse containing the serialized articles with
        appropriate Content-Type and Content-Disposition headers.

    Raises:
        HTTPException: 400 if the format parameter is not 'csv' or 'json'.
    """
    if format not in ("csv", "json"):
        raise HTTPException(
            status_code=400,
            detail="Format must be 'csv' or 'json'",
        )

    articles = db.query(Article).all()

    if format == "csv":
        return StreamingResponse(
            content=generate_csv(articles),
            media_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="articles.csv"',
            },
        )

    # JSON format
    articles_data = [article_to_dict(article) for article in articles]
    json_content = json.dumps(articles_data, ensure_ascii=False, indent=2)

    def generate_json() -> Generator[str, None, None]:
        yield json_content

    return StreamingResponse(
        content=generate_json(),
        media_type="application/json",
        headers={
            "Content-Disposition": 'attachment; filename="articles.json"',
        },
    )
