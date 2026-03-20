"""Recommendations API endpoint for similar articles."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.article import get_article
from app.ml.similarity import find_similar_articles

logger = logging.getLogger(__name__)

router = APIRouter()


class SimilarArticleSchema(BaseModel):
    """Schema for a single similar article result."""

    id: int
    title: str
    similarity_score: float

    class Config:
        from_attributes = True


class SimilarArticlesResponse(BaseModel):
    """Response schema for the similar articles endpoint."""

    article_id: int
    similar_articles: List[SimilarArticleSchema]


@router.get(
    "/{article_id}/similar",
    response_model=SimilarArticlesResponse,
    summary="Get similar articles",
)
def get_similar_articles(
    article_id: int,
    limit: int = Query(default=5, ge=1, le=50, description="Maximum number of similar articles to return"),
    db: Session = Depends(get_db),
) -> SimilarArticlesResponse:
    """Return the most similar articles to the given article."""
    article = get_article(db, article_id)
    if article is None:
        logger.warning("Article %d not found for recommendations.", article_id)
        raise HTTPException(
            status_code=404,
            detail=f"Article with id={article_id} not found.",
        )

    logger.info(
        "Computing similar articles for article_id=%d with limit=%d",
        article_id,
        limit,
    )

    similar = find_similar_articles(db, article_id, limit=limit)

    similar_schemas = [
        SimilarArticleSchema(
            id=item.id,
            title=item.title,
            similarity_score=round(item.similarity_score, 6),
        )
        for item in similar
    ]

    return SimilarArticlesResponse(
        article_id=article_id,
        similar_articles=similar_schemas,
    )
