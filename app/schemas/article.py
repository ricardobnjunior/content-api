"""Pydantic schemas for Article."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.category import CategoryResponse


class ArticleCreate(BaseModel):
    """Schema for creating a new article."""

    title: str
    body: str
    author: str
    status: Optional[str] = "draft"
    category_ids: list[int] = []


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article."""

    title: Optional[str] = None
    body: Optional[str] = None
    author: Optional[str] = None
    status: Optional[str] = None
    category_ids: list[int] = []


class ArticleResponse(BaseModel):
    """Schema for article responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    author: str
    status: str
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryResponse] = []


class ArticleList(BaseModel):
    """Schema for a list of articles."""

    model_config = ConfigDict(from_attributes=True)

    items: list[ArticleResponse]
    total: int
