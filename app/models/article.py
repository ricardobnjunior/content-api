"""SQLAlchemy model for Article."""

import enum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class ArticleStatus(str, enum.Enum):
    """Status of an article."""

    draft = "draft"
    published = "published"


class Article(Base):
    """Article ORM model.

    Attributes:
        id: Primary key.
        title: Article title, max 200 chars.
        body: Full article content.
        author: Author name, max 100 chars.
        status: Draft or published.
        created_at: Timestamp set on creation.
        updated_at: Timestamp updated on modification.
    """

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    status = Column(SQLEnum(ArticleStatus), default=ArticleStatus.draft, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
