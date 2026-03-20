"""Endpoint for ML-powered category suggestions."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ml.classifier import suggest_categories
from app.database import get_db
from app.models.article import Article

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


class CategorySuggestion(BaseModel):
    """A single category suggestion with a confidence score."""

    category_id: int
    category_name: str
    confidence: float


class SuggestionsResponse(BaseModel):
    """Response model for the category suggestions endpoint."""

    article_id: int
    suggestions: list[CategorySuggestion]


@router.get("/categories/{article_id}", response_model=SuggestionsResponse)
def get_category_suggestions(
    article_id: int,
    limit: int = 3,
    db: Session = Depends(get_db),
) -> SuggestionsResponse:
    """Return ML-powered category suggestions for the given article."""
    # Fetch target article
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    target_text = f"{article.title} {article.content or ''}"

    # Fetch all articles that have at least one category assigned
    categorized_articles_db: list[Article] = (
        db.query(Article)
        .filter(Article.id != article_id)
        .filter(Article.categories.any())
        .all()
    )

    # Build list of {text, category_id, category_name} — one entry per article-category pair
    classifier_input: list[dict[str, Any]] = []
    for art in categorized_articles_db:
        art_text = f"{art.title} {art.content or ''}"
        for cat in art.categories:
            classifier_input.append(
                {
                    "text": art_text,
                    "category_id": cat.id,
                    "category_name": cat.name,
                }
            )

    logger.debug(
        "Suggesting categories for article %d using %d categorized article-category pairs.",
        article_id,
        len(classifier_input),
    )

    suggestions_raw = suggest_categories(target_text, classifier_input, limit=limit)

    suggestions = [CategorySuggestion(**s) for s in suggestions_raw]

    return SuggestionsResponse(article_id=article_id, suggestions=suggestions)
