"""Pydantic schemas for articles."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ArticleCreate(BaseModel):
    """Schema for creating a new article.

    Attributes:
        title: Article title.
        content: Article body content.
        status: Publication status.
        category_ids: Optional list of category IDs.
    """

    title: str
    content: Optional[str] = None
    status: str = "draft"
    category_ids: Optional[List[int]] = None


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article.

    Attributes:
        title: New title (optional).
        content: New content (optional).
        status: New status (optional).
        category_ids: New category IDs (optional).
    """

    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    category_ids: Optional[List[int]] = None


class ArticleResponse(BaseModel):
    """Schema for article API responses.

    Attributes:
        id: Article identifier.
        title: Article title.
        content: Article content.
        status: Publication status.
        image_url: Optional URL to article image.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: int
    title: str
    content: Optional[str] = None
    status: str
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    """Pagination metadata.

    Attributes:
        total: Total number of items.
        page: Current page number.
        per_page: Items per page.
        total_pages: Total number of pages.
    """

    total: int
    page: int
    per_page: int
    total_pages: int


class ArticleList(BaseModel):
    """Paginated list of articles.

    Attributes:
        items: List of articles.
        meta: Pagination metadata.
    """

    items: List[ArticleResponse]
    meta: PaginationMeta
