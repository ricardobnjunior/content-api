"""API endpoint for AI-powered category suggestions."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.classifier import classify_article
from app.crud.article import get_article
from app.database import get_db
from app.models.category import Category

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


class SuggestionItem(BaseModel):
    """A single category suggestion item in the API response.

    Attributes:
        category_id: The database ID of the suggested category.
        category_name: The human-readable name of the category.
        confidence: Confidence score between 0.0 and 1.0.
    """

    category_id: int
    category_name: str
    confidence: float


class SuggestionsResponse(BaseModel):
    """Response model for the category suggestions endpoint.

    Attributes:
        article_id: The ID of the article being classified.
        suggestions: Ordered list of category suggestions by confidence.
    """

    article_id: int
    suggestions: list[SuggestionItem]


@router.get("/categories/{article_id}", response_model=SuggestionsResponse)
def get_category_suggestions(
    article_id: int,
    limit: int = Query(default=3, ge=1, description="Maximum number of suggestions"),
    db: Session = Depends(get_db),
) -> SuggestionsResponse:
    """Suggest categories for an article using an LLM classifier.

    Loads the article and all existing categories from the database, then
    calls the LLM-based classifier to return ranked category suggestions
    with confidence scores.

    Args:
        article_id: The ID of the article to classify.
        limit: Maximum number of suggestions to return (default 3, minimum 1).
        db: Database session injected by FastAPI dependency injection.

    Returns:
        SuggestionsResponse with article_id and list of suggestion items.

    Raises:
        HTTPException 404: If the article is not found.
        HTTPException 500: If the LLM API call fails or returns invalid data.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    categories = db.query(Category).all()
    if not categories:
        return SuggestionsResponse(article_id=article_id, suggestions=[])

    category_names = [cat.name for cat in categories]
    name_to_id = {cat.name: cat.id for cat in categories}

    try:
        raw_suggestions = classify_article(
            title=article.title,
            content=article.content or "",
            category_names=category_names,
            limit=limit,
        )
    except Exception as exc:
        logger.error("LLM classifier failed for article %d: %s", article_id, exc)
        raise HTTPException(
            status_code=500,
            detail=f"LLM classification failed: {exc}",
        ) from exc

    suggestion_items = []
    for suggestion in raw_suggestions:
        cat_name = suggestion["category_name"]
        cat_id = name_to_id.get(cat_name)
        if cat_id is None:
            logger.warning("Classifier returned unknown category '%s', skipping", cat_name)
            continue
        suggestion_items.append(
            SuggestionItem(
                category_id=cat_id,
                category_name=cat_name,
                confidence=suggestion["confidence"],
            )
        )

    return SuggestionsResponse(article_id=article_id, suggestions=suggestion_items)
