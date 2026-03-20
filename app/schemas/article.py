"""Article Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel


class CategoryBrief(BaseModel):
    """Brief category representation used within article responses.

    Attributes:
        id: Category primary key.
        name: Category name.
    """

    id: int
    name: str

    model_config = {"from_attributes": True}


class ArticleCreate(BaseModel):
    """Schema for creating a new article.

    Attributes:
        title: Article title.
        content: Article body content.
        status: Publication status, defaults to 'draft'.
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
        title: New article title.
        content: New article body content.
        status: New publication status.
        category_ids: New list of category IDs.
        image_url: New image URL (used internally by upload endpoint).
    """

    title: str | None = None
    content: str | None = None
    status: str | None = None
    category_ids: list[int] | None = None
    image_url: str | None = None


class ArticleResponse(BaseModel):
    """Schema for article API responses.

    Attributes:
        id: Article primary key.
        title: Article title.
        content: Article body content.
        status: Publication status.
        image_url: Optional URL path to the article image.
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
    categories: list[CategoryBrief] = []

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses.

    Attributes:
        total: Total number of items.
        page: Current page number (1-indexed).
        per_page: Number of items per page.
        pages: Total number of pages.
    """

    total: int
    page: int
    per_page: int
    pages: int


class ArticleList(BaseModel):
    """Paginated list of articles.

    Attributes:
        items: List of article responses for the current page.
        meta: Pagination metadata.
    """

    items: list[ArticleResponse]
    meta: PaginationMeta
