"""Pydantic schemas for Article."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.article import ArticleStatus


class ArticleCreate(BaseModel):
    """Schema for creating a new article.

    Attributes:
        title: Article title, 1–200 characters.
        body: Full article content, at least 1 character.
        author: Author name, 1–100 characters.
        status: Article status, defaults to draft.
    """

    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    status: ArticleStatus = ArticleStatus.draft


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article (all fields optional).

    Attributes:
        title: New title, 1–200 characters.
        body: New content, at least 1 character.
        author: New author name, 1–100 characters.
        status: New status.
    """

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    body: Optional[str] = Field(default=None, min_length=1)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
    status: Optional[ArticleStatus] = None


class ArticleResponse(BaseModel):
    """Schema for returning an article in API responses.

    Attributes:
        id: Article primary key.
        title: Article title.
        body: Article content.
        author: Author name.
        status: Current status.
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
    """Schema for a paginated list of articles.

    Attributes:
        items: List of article responses.
        total: Total number of articles in the database.
    """

    items: list[ArticleResponse]
    total: int
