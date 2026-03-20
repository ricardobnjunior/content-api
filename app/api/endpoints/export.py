"""Export endpoint for downloading articles as CSV or JSON."""

import csv
import io
import json
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article

router = APIRouter()


def article_to_dict(article: Article) -> dict:
    """Convert an Article SQLAlchemy instance to a plain dict.

    Args:
        article: The Article ORM instance.

    Returns:
        A dict with all column values. Datetime fields are converted
        to ISO 8601 strings.
    """
    result = {}
    for column in Article.__table__.columns:
        value = getattr(article, column.name)
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        result[column.name] = value
    return result


def generate_csv(articles: list) -> Generator[str, None, None]:
    """Generate CSV rows as a streaming generator.

    Yields the header row first, then one row per article.

    Args:
        articles: List of Article ORM instances.

    Yields:
        CSV-formatted string chunks.
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
        row_dict = article_to_dict(article)
        writer.writerow([row_dict.get(col) for col in columns])
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)


@router.get("/articles", summary="Export all articles")
def export_articles(
    format: str = Query(..., description="Export format: 'csv' or 'json'"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Export all articles in CSV or JSON format.

    Args:
        format: The desired export format. Must be 'csv' or 'json'.
        db: SQLAlchemy database session (injected).

    Returns:
        A StreamingResponse with the serialized articles and appropriate
        Content-Type and Content-Disposition headers.

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
            generate_csv(articles),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="articles.csv"'},
        )

    # JSON format
    data = [article_to_dict(article) for article in articles]
    json_bytes = json.dumps(data).encode("utf-8")

    def json_generator():
        yield json_bytes

    return StreamingResponse(
        json_generator(),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="articles.json"'},
    )
