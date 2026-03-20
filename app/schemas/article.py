"""Pydantic schemas for Article endpoints."""

import math
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.article import ArticleStatus


class CategoryRef(BaseModel):
    """Minimal category reference used inside article responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ArticleCreate(BaseModel):
    """Schema for creating a new article."""

    title: str
    body: str
    status: ArticleStatus = ArticleStatus.draft
    author: str
    category_ids: list[int] = []


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article."""

    title: str | None = None
    body: str | None = None
    status: ArticleStatus | None = None
    author: str | None = None
    category_ids: list[int] | None = None


class ArticleResponse(BaseModel):
    """Schema for a single article in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    status: ArticleStatus
    author: str
    categories: list[CategoryRef] = []
    created_at: datetime
    updated_at: datetime


class PaginationMeta(BaseModel):
    """Pagination metadata included in list responses."""

    total: int
    page: int
    per_page: int
    pages: int


class ArticleList(BaseModel):
    """Schema for paginated list of articles."""

    items: list[ArticleResponse]
    meta: PaginationMeta
