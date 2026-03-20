"""Article SQLAlchemy model."""

import enum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class ArticleStatus(str, enum.Enum):
    """Enumeration of possible article statuses."""

    draft = "draft"
    published = "published"


class Article(Base):
    """SQLAlchemy ORM model representing a news/blog article."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    status = Column(SQLEnum(ArticleStatus), default=ArticleStatus.draft, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
