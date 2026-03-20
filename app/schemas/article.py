"""Pydantic v2 schemas for Article resources."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.article import ArticleStatus


class ArticleCreate(BaseModel):
    """Schema for creating a new article.

    Attributes:
        title: Article title, max 200 characters.
        body: Full article body text.
        author: Author name, max 100 characters.
        status: Publication status; defaults to draft.
    """

    title: str = Field(..., max_length=200, min_length=1)
    body: str
    author: str = Field(..., max_length=100)
    status: ArticleStatus = ArticleStatus.draft


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article (all fields optional).

    Attributes:
        title: New title, max 200 characters.
        body: New body text.
        author: New author name, max 100 characters.
        status: New publication status.
    """

    title: Optional[str] = Field(default=None, max_length=200, min_length=1)
    body: Optional[str] = None
    author: Optional[str] = Field(default=None, max_length=100)
    status: Optional[ArticleStatus] = None


class ArticleResponse(BaseModel):
    """Schema for article API responses.

    Attributes:
        id: Article primary key.
        title: Article title.
        body: Full article body text.
        author: Author name.
        status: Publication status.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    author: str
    status: ArticleStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ArticleList(BaseModel):
    """Schema for paginated article list responses.

    Attributes:
        items: List of article responses.
        total: Total count of articles matching the query.
    """

    items: list[ArticleResponse]
    total: int
