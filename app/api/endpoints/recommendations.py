"""Recommendations endpoint — returns AI-powered similar articles."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.similarity import find_similar_articles
from app.crud.article import get_article, get_articles
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class SimilarArticleItem(BaseModel):
    """A single similar article result with its similarity score.

    Attributes:
        id: The article's unique identifier.
        title: The article's title.
        similarity_score: A float between 0 and 1 indicating similarity.
    """

    id: int
    title: str
    similarity_score: float


class SimilarArticlesResponse(BaseModel):
    """Response model for the similar articles endpoint.

    Attributes:
        article_id: The ID of the target article.
        similar_articles: Ranked list of similar articles with scores.
    """

    article_id: int
    similar_articles: List[SimilarArticleItem]


@router.get(
    "/{article_id}/similar",
    response_model=SimilarArticlesResponse,
    summary="Get similar articles",
    description=(
        "Returns the most similar published articles to the given article, "
        "ranked by AI-computed similarity score."
    ),
)
def get_similar_articles(
    article_id: int,
    limit: int = Query(default=5, ge=1, le=50, description="Maximum number of similar articles to return"),
    db: Session = Depends(get_db),
) -> SimilarArticlesResponse:
    """Return the most similar published articles to the specified article.

    Args:
        article_id: The ID of the target article to find similar articles for.
        limit: Maximum number of similar articles to return (1–50, default 5).
        db: Database session injected by FastAPI dependency injection.

    Returns:
        SimilarArticlesResponse with the target article ID and ranked list
        of similar articles including their similarity scores.

    Raises:
        HTTPException: 404 if the article is not found.
        HTTPException: 500 if the LLM API call fails or returns invalid data.
    """
    # Fetch the target article
    target_article = get_article(db, article_id)
    if target_article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    # Fetch all published articles, excluding the target
    all_articles = get_articles(db, status="published")
    candidates = [a for a in all_articles if a.id != article_id]

    # No candidates — return empty response immediately without calling LLM
    if not candidates:
        return SimilarArticlesResponse(
            article_id=article_id,
            similar_articles=[],
        )

    # Call LLM to find similar articles
    try:
        similar_results = find_similar_articles(
            target_article=target_article,
            candidate_articles=candidates,
            limit=limit,
        )
    except (ValueError, RuntimeError) as exc:
        logger.error("Similarity computation failed for article %d: %s", article_id, exc)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute article similarity: {exc}",
        ) from exc

    # Build a lookup map for candidate article titles
    article_title_map = {a.id: a.title for a in candidates}

    similar_items = [
        SimilarArticleItem(
            id=result["id"],
            title=article_title_map.get(result["id"], ""),
            similarity_score=result["similarity_score"],
        )
        for result in similar_results
        if result["id"] in article_title_map
    ]

    return SimilarArticlesResponse(
        article_id=article_id,
        similar_articles=similar_items,
    )
