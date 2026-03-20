"""API endpoint for AI-powered category suggestions."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.classifier import suggest_categories
from app.config import settings
from app.crud.article import get_article
from app.database import get_db
from app.models.category import Category

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


class CategorySuggestionItem(BaseModel):
    """A single category suggestion item in the API response.

    Attributes:
        category_id: The database ID of the suggested category.
        category_name: The human-readable name of the category.
        confidence: LLM confidence score between 0.0 and 1.0.
    """

    category_id: int
    category_name: str
    confidence: float


class CategorySuggestionsResponse(BaseModel):
    """Response schema for the category suggestions endpoint.

    Attributes:
        article_id: The ID of the article being classified.
        suggestions: Ordered list of category suggestions (highest confidence first).
    """

    article_id: int
    suggestions: list[CategorySuggestionItem]


@router.get(
    "/categories/{article_id}",
    response_model=CategorySuggestionsResponse,
    summary="Suggest categories for an article",
    description=(
        "Uses an LLM to suggest the most relevant categories for an article "
        "based on its title and content. Returns suggestions sorted by confidence score."
    ),
)
def get_category_suggestions(
    article_id: int,
    limit: int = Query(default=3, ge=1, description="Maximum number of suggestions to return"),
    db: Session = Depends(get_db),
) -> CategorySuggestionsResponse:
    """Return AI-generated category suggestions for a given article.

    Loads the article from the database, retrieves all existing categories,
    and calls the LLM classifier to rank them by relevance. Returns the
    top ``limit`` suggestions sorted by confidence score.

    Args:
        article_id: The database ID of the article to classify.
        limit: Maximum number of suggestions to return (default 3, minimum 1).
        db: SQLAlchemy database session (injected by FastAPI).

    Returns:
        CategorySuggestionsResponse with article_id and ranked suggestions.

    Raises:
        HTTPException 404: If the article with the given ID does not exist.
        HTTPException 500: If the LLM API call fails.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail=f"Article {article_id} not found.")

    categories = db.query(Category).all()

    if not categories:
        return CategorySuggestionsResponse(article_id=article_id, suggestions=[])

    category_names = [c.name for c in categories]
    name_to_category = {c.name: c for c in categories}

    try:
        raw_suggestions = suggest_categories(
            title=article.title,
            content=article.content or "",
            category_names=category_names,
            settings=settings,
        )
    except (RuntimeError, Exception) as exc:
        logger.error("Category suggestion failed for article %d: %s", article_id, exc)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate category suggestions: {exc}",
        ) from exc

    suggestion_items: list[CategorySuggestionItem] = []
    for suggestion in raw_suggestions:
        name = suggestion["category_name"]
        matched_category = name_to_category.get(name)
        if matched_category is None:
            continue
        suggestion_items.append(
            CategorySuggestionItem(
                category_id=matched_category.id,
                category_name=name,
                confidence=suggestion["confidence"],
            )
        )

    return CategorySuggestionsResponse(
        article_id=article_id,
        suggestions=suggestion_items[:limit],
    )
