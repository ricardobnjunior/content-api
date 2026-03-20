"""Pydantic schemas for Article and Category resources."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    """Schema for category in article responses.

    Attributes:
        id: Category identifier.
        name: Category name.
    """

    id: int
    name: str

    model_config = {"from_attributes": True}


class ArticleCreate(BaseModel):
    """Schema for creating a new article.

    Attributes:
        title: Article title.
        content: Article body text.
        status: Publication status (default: draft).
        category_ids: List of category IDs to associate.
    """

    title: str
    content: str
    status: str = "draft"
    category_ids: list[int] = []


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article.

    All fields are optional — only provided fields are updated.

    Attributes:
        title: Updated article title.
        content: Updated article body text.
        status: Updated publication status.
        category_ids: Updated list of category IDs.
        image_url: Updated image URL.
    """

    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    category_ids: Optional[list[int]] = None
    image_url: Optional[str] = None


class ArticleResponse(BaseModel):
    """Schema for article responses.

    Attributes:
        id: Article identifier.
        title: Article title.
        content: Article body text.
        status: Publication status.
        image_url: Optional URL to the article's cover image.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        categories: List of associated categories.
    """

    id: int
    title: str
    content: str
    status: str
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryResponse] = []

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    """Pagination metadata.

    Attributes:
        total: Total number of items.
        page: Current page number.
        per_page: Items per page.
        pages: Total number of pages.
    """

    total: int
    page: int
    per_page: int
    pages: int


class ArticleList(BaseModel):
    """Paginated list of articles.

    Attributes:
        items: List of articles on the current page.
        meta: Pagination metadata.
    """

    items: list[ArticleResponse]
    meta: PaginationMeta
