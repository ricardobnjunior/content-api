"""Article ORM model."""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.database import Base

# Association table for many-to-many between articles and categories
article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class ArticleStatus(str, enum.Enum):
    """Possible publication statuses for an article."""

    draft = "draft"
    published = "published"


class Article(Base):
    """ORM model representing a news/blog article."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(Enum(ArticleStatus), nullable=False, default=ArticleStatus.draft)
    author = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    categories = relationship(
        "Category",
        secondary=article_categories,
        back_populates="articles",
    )
