"""Pydantic schemas for article API."""

import math
from typing import Optional

from pydantic import BaseModel

from app.models.article import ArticleStatus


class CategoryResponse(BaseModel):
    """Schema for category in article response."""

    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class ArticleCreate(BaseModel):
    """Schema for creating an article."""

    title: str
    body: str
    status: ArticleStatus = ArticleStatus.draft
    author: str
    category_ids: list[int] = []


class ArticleUpdate(BaseModel):
    """Schema for updating an article."""

    title: Optional[str] = None
    body: Optional[str] = None
    status: Optional[ArticleStatus] = None
    author: Optional[str] = None
    category_ids: Optional[list[int]] = None


class ArticleResponse(BaseModel):
    """Schema for article API response."""

    id: int
    title: str
    body: str
    status: ArticleStatus
    author: str
    categories: list[CategoryResponse] = []

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    total: int
    page: int
    per_page: int
    pages: int


class ArticleList(BaseModel):
    """Schema for paginated list of articles."""

    items: list[ArticleResponse]
    meta: PaginationMeta
