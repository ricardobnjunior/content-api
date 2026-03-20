"""Recommendations endpoint for AI-powered similar article discovery."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.similarity import get_similar_articles
from app.crud.article import get_article, get_articles
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class SimilarArticleItem(BaseModel):
    """A single similar article result with its similarity score."""

    id: int
    title: str
    similarity_score: float


class SimilarArticlesResponse(BaseModel):
    """Response model for the similar articles endpoint."""

    article_id: int
    similar_articles: List[SimilarArticleItem]


@router.get(
    "/{article_id}/similar",
    response_model=SimilarArticlesResponse,
    summary="Get similar articles",
)
def get_similar(
    article_id: int,
    limit: int = 5,
    db: Session = Depends(get_db),
) -> SimilarArticlesResponse:
    """Return similar articles for the given article ID."""
    # Fetch target article
    target = get_article(db, article_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Article not found")

    # Fetch all published articles, excluding the target
    all_articles = get_articles(db)
    candidates = [
        a for a in all_articles
        if a.id != article_id and getattr(a, "status", None) == "published"
    ]

    # Short-circuit: no candidates to compare
    if not candidates:
        return SimilarArticlesResponse(article_id=article_id, similar_articles=[])

    # Build a lookup map for enriching results with titles
    article_map = {a.id: a for a in candidates}

    # Call LLM similarity engine
    try:
        raw_results = get_similar_articles(
            target_article=target,
            candidate_articles=candidates,
            limit=limit,
        )
    except (ValueError, RuntimeError) as exc:
        logger.error("Similarity engine error for article %d: %s", article_id, exc)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute article similarity: {exc}",
        ) from exc

    # Enrich results with article titles
    similar_items: List[SimilarArticleItem] = []
    for result in raw_results:
        candidate = article_map.get(result["id"])
        if candidate is None:
            continue
        similar_items.append(
            SimilarArticleItem(
                id=result["id"],
                title=candidate.title,
                similarity_score=result["similarity_score"],
            )
        )

    return SimilarArticlesResponse(article_id=article_id, similar_articles=similar_items)
