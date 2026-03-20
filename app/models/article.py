"""Article SQLAlchemy model."""

import enum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.sql import func



class ArticleStatus(str, enum.Enum):
    """Status enum for articles."""

    draft = "draft"
    published = "published"


class Article(Base):
    """SQLAlchemy model for articles."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    status = Column(SQLEnum(ArticleStatus), default=ArticleStatus.draft, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
