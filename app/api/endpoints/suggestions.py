"""Endpoint for AI-powered category suggestions."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session


router = APIRouter(prefix="/suggestions", tags=["suggestions"])


class CategorySuggestionItem(BaseModel):
    """A single category suggestion with its confidence score.

    Attributes:
        category_id: The database ID of the suggested category.
        category_name: The human-readable name of the category.
        confidence: LLM confidence score between 0.0 and 1.0.
    """

    category_id: int
    category_name: str
    confidence: float


class SuggestionsResponse(BaseModel):
    """Response model for the category suggestions endpoint.

    Attributes:
        article_id: The ID of the article that was classified.
        suggestions: Ordered list of category suggestions.
    """

    article_id: int
    suggestions: list[CategorySuggestionItem]


@router.get("/categories/{article_id}", response_model=SuggestionsResponse)
def suggest_categories(
    article_id: int,
    limit: int = Query(default=3, ge=1, le=20, description="Maximum number of suggestions to return"),
    db: Session = Depends(get_db),
) -> Any:
    """Suggest relevant categories for an article using an LLM.

    Fetches the article and all existing categories from the database, then
    calls the OpenRouter-backed classifier to determine the most relevant
    categories with confidence scores.

    Args:
        article_id: The primary key of the article to classify.
        limit: Maximum number of suggestions to return (1–20, default 3).
        db: SQLAlchemy database session (injected via Depends).

    Returns:
        SuggestionsResponse: Article ID plus an ordered list of suggestions.

    Raises:
        HTTPException 404: If the article is not found.
        HTTPException 500: If the LLM API call fails or returns invalid data.
    """
    # Fetch article — 404 if not found
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail=f"Article {article_id} not found")

    # Fetch all categories
    categories = db.query(Category).all()
    if not categories:
        return SuggestionsResponse(article_id=article_id, suggestions=[])

    # Build name→id map for result assembly
    name_to_category: dict[str, Category] = {cat.name: cat for cat in categories}
    category_names = list(name_to_category.keys())

    # Call classifier
    from app.ai.classifier import classify_article  # local import to allow easy mocking

    try:
        raw_suggestions = classify_article(
            title=article.title,
            content=article.content or "",
            category_names=category_names,
            limit=limit,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM classification failed: {exc}") from exc

    # Map LLM-suggested names back to DB category records
    result_items: list[CategorySuggestionItem] = []
    for suggestion in raw_suggestions:
        cat_name = suggestion["category_name"]
        confidence = suggestion["confidence"]
        matched_cat = name_to_category.get(cat_name)
        if matched_cat is None:
            # LLM hallucinated a category name — skip it
            continue
        result_items.append(
            CategorySuggestionItem(
                category_id=matched_cat.id,
                category_name=cat_name,
                confidence=confidence,
            )
        )

    return SuggestionsResponse(article_id=article_id, suggestions=result_items)
