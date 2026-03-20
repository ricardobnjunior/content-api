"""API endpoint for AI-powered article similarity recommendations."""

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
    """A single similar article with its similarity score.

    Attributes:
        id: The article's unique identifier.
        title: The article's title.
        similarity_score: Float between 0 and 1 representing similarity.
    """

    id: int
    title: str
    similarity_score: float


class SimilarArticlesResponse(BaseModel):
    """Response model for the similar articles endpoint.

    Attributes:
        article_id: The ID of the target article.
        similar_articles: List of similar articles with scores.
    """

    article_id: int
    similar_articles: List[SimilarArticleItem]


@router.get("/{article_id}/similar", response_model=SimilarArticlesResponse)
def get_similar_articles(
    article_id: int,
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
) -> SimilarArticlesResponse:
    """Return articles most similar to the given article using LLM analysis.

    Fetches the target article and all published articles from the database,
    then asks the LLM to rank candidates by content similarity.

    Args:
        article_id: The ID of the article to find similarities for.
        limit: Maximum number of similar articles to return (default 5, max 50).
        db: SQLAlchemy database session (injected via Depends).

    Returns:
        SimilarArticlesResponse containing the article_id and ranked similar articles.

    Raises:
        HTTPException 404: If the target article does not exist.
        HTTPException 500: If the LLM API call fails or returns invalid data.
    """
    # Fetch the target article
    target_article = get_article(db, article_id)
    if target_article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    # Fetch all published articles
    all_articles = get_articles(db)
    published_articles = [
        a for a in all_articles if a.status == "published"
    ]

    # Exclude the target article from candidates
    candidate_articles = [a for a in published_articles if a.id != article_id]

    if not candidate_articles:
        logger.info(
            "No candidate articles available for article_id=%d, returning empty list",
            article_id,
        )
        return SimilarArticlesResponse(
            article_id=article_id,
            similar_articles=[],
        )

    # Build a lookup map for article titles
    article_map = {a.id: a for a in candidate_articles}

    # Call the LLM similarity engine
    try:
        similarity_results = find_similar_articles(
            target_article=target_article,
            candidate_articles=candidate_articles,
            limit=limit,
        )
    except (ValueError, RuntimeError) as exc:
        logger.error(
            "Similarity computation failed for article_id=%d: %s", article_id, exc
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute article similarity: {exc}",
        ) from exc

    # Enrich results with article titles
    similar_items = []
    for result in similarity_results:
        aid = result["id"]
        if aid in article_map:
            similar_items.append(
                SimilarArticleItem(
                    id=aid,
                    title=article_map[aid].title,
                    similarity_score=result["similarity_score"],
                )
            )

    return SimilarArticlesResponse(
        article_id=article_id,
        similar_articles=similar_items,
    )
