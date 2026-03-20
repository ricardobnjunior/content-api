"""Export endpoint for downloading articles as CSV or JSON."""

import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article

router = APIRouter()


def _article_to_dict(article: Article) -> dict:
    """Convert an Article ORM instance to a serializable dictionary.

    Args:
        article: SQLAlchemy Article model instance.

    Returns:
        Dictionary with all article column values, datetime fields as ISO strings.
    """
    result = {}
    for column in Article.__table__.columns:
        value = getattr(article, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result


@router.get("/articles")
def export_articles(
    format: str = Query(..., description="Export format: 'csv' or 'json'"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Export all articles as CSV or JSON file download.

    Args:
        format: The export format, must be 'csv' or 'json'.
        db: SQLAlchemy database session injected by FastAPI.

    Returns:
        StreamingResponse with the file contents and appropriate headers.

    Raises:
        HTTPException: 400 if format is not 'csv' or 'json'.
    """
    if format not in ("csv", "json"):
        raise HTTPException(
            status_code=400,
            detail="Format must be 'csv' or 'json'",
        )

    articles = db.query(Article).all()
    article_dicts = [_article_to_dict(article) for article in articles]

    if format == "csv":
        return _build_csv_response(article_dicts)
    else:
        return _build_json_response(article_dicts)


def _build_csv_response(article_dicts: list[dict]) -> StreamingResponse:
    """Build a StreamingResponse containing CSV data.

    Args:
        article_dicts: List of article dictionaries with serializable values.

    Returns:
        StreamingResponse with text/csv content type and attachment header.
    """
    fieldnames = ["id", "title", "content", "status", "image_url", "created_at", "updated_at"]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(fieldnames)

    for article in article_dicts:
        writer.writerow([article.get(field) for field in fieldnames])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="articles.csv"'},
    )


def _build_json_response(article_dicts: list[dict]) -> StreamingResponse:
    """Build a StreamingResponse containing JSON data.

    Args:
        article_dicts: List of article dictionaries with serializable values.

    Returns:
        StreamingResponse with application/json content type and attachment header.
    """
    json_content = json.dumps(article_dicts)

    return StreamingResponse(
        iter([json_content]),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="articles.json"'},
    )
