"""Pydantic schemas for Article endpoints."""

from datetime import datetime

from pydantic import BaseModel

from app.models.article import ArticleStatus


class CategoryRef(BaseModel):
    """Minimal category reference used inside article responses."""

    id: int
    name: str

    model_config = {"from_attributes": True}


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
    """Schema returned by article endpoints."""

    id: int
    title: str
    body: str
    status: ArticleStatus
    author: str
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryRef] = []

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    """Pagination metadata included in list responses."""

    total: int
    page: int
    per_page: int
    pages: int


class ArticleList(BaseModel):
    """Paginated list of articles with metadata."""

    items: list[ArticleResponse]
    meta: PaginationMeta
