"""Suggestions API endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db

router = APIRouter()


class SuggestionResponse(BaseModel):
    suggestions: List[str]


@router.get("/", response_model=SuggestionResponse)
def get_suggestions(db: Session = Depends(get_db)):
    """Get content suggestions."""
    return SuggestionResponse(suggestions=[])
