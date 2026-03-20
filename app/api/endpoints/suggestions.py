"""Endpoint for AI-powered category suggestions for articles."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.classifier import classify_article
from app.crud.article import get_article
from app.database import get_db
from app.models.category import Category

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


class CategorySuggestionItem(BaseModel):
    """A single category suggestion with confidence score.

    Attributes:
        category_id: The database ID of the suggested category.
        category_name: The display name of the suggested category.
        confidence: LLM confidence score between 0.0 and 1.0.
    """

    category_id: int
    category_name: str
    confidence: float


class SuggestionsResponse(BaseModel):
    """Response model for category suggestions endpoint.

    Attributes:
        article_id: The ID of the article that was classified.
        suggestions: List of category suggestions ordered by confidence descending.
    """

    article_id: int
    suggestions: List[CategorySuggestionItem]


@router.get(
    "/categories/{article_id}",
    response_model=SuggestionsResponse,
    summary="Get AI-powered category suggestions for an article",
    description=(
        "Uses an LLM to suggest the most relevant categories for an article "
        "based on its title and content. Returns suggestions with confidence scores."
    ),
)
def get_category_suggestions(
    article_id: int,
    limit: int = Query(default=3, ge=1, description="Maximum number of suggestions to return"),
    db: Session = Depends(get_db),
) -> SuggestionsResponse:
    """Return AI-generated category suggestions for an article.

    Fetches the article and all categories from the database, sends them to
    the LLM classifier, and returns the top suggestions sorted by confidence.

    Args:
        article_id: The ID of the article to classify.
        limit: Maximum number of suggestions to return (default 3, minimum 1).
        db: Database session injected by FastAPI.

    Returns:
        SuggestionsResponse with the article ID and list of category suggestions.

    Raises:
        HTTPException 404: If the article does not exist.
        HTTPException 500: If the LLM API call fails or returns malformed data.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    categories = db.query(Category).all()
    if not categories:
        logger.info("No categories in DB; returning empty suggestions for article %d", article_id)
        return SuggestionsResponse(article_id=article_id, suggestions=[])

    category_name_to_id: dict[str, int] = {cat.name: cat.id for cat in categories}
    category_names: list[str] = list(category_name_to_id.keys())

    try:
        raw_suggestions = classify_article(
            title=article.title,
            content=article.content or "",
            category_names=category_names,
        )
    except Exception as exc:
        logger.error("LLM classification failed for article %d: %s", article_id, exc)
        raise HTTPException(
            status_code=500,
            detail=f"LLM classification failed: {exc}",
        ) from exc

    matched_suggestions: list[CategorySuggestionItem] = []
    for suggestion in raw_suggestions:
        name = suggestion.get("category_name", "")
        confidence = suggestion.get("confidence", 0.0)
        category_id = category_name_to_id.get(name)
        if category_id is None:
            logger.debug("LLM suggested unknown category %r — skipping", name)
            continue
        matched_suggestions.append(
            CategorySuggestionItem(
                category_id=category_id,
                category_name=name,
                confidence=confidence,
            )
        )

    matched_suggestions.sort(key=lambda s: s.confidence, reverse=True)
    limited_suggestions = matched_suggestions[:limit]

    return SuggestionsResponse(article_id=article_id, suggestions=limited_suggestions)
