"""Pydantic schemas for Article CRUD operations."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.article import ArticleStatus


class ArticleCreate(BaseModel):
    """Schema for creating a new article.

    Attributes:
        title: Article title, max 200 characters.
        body: Article body text.
        author: Author name, max 100 characters.
        status: Publication status, defaults to draft.
    """

    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    status: ArticleStatus = ArticleStatus.draft


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article.

    All fields are optional — only provided fields will be updated.

    Attributes:
        title: New article title, max 200 characters.
        body: New article body text.
        author: New author name, max 100 characters.
        status: New publication status.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[ArticleStatus] = None


class ArticleResponse(BaseModel):
    """Schema for article responses.

    Attributes:
        id: Article primary key.
        title: Article title.
        body: Article body text.
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
    """Schema for paginated list of articles.

    Attributes:
        items: List of articles.
        total: Total number of articles in the database.
    """

    items: list[ArticleResponse]
    total: int
