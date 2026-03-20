"""Article model definition."""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


# Association table for many-to-many relationship between articles and categories
article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE")),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE")),
)


class ArticleStatus(str, enum.Enum):
    """Enumeration of possible article statuses."""

    draft = "draft"
    published = "published"
    archived = "archived"


class Article(Base):
    """SQLAlchemy model for articles."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    status = Column(
        Enum(ArticleStatus),
        nullable=False,
        default=ArticleStatus.draft,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    categories = relationship(
        "Category",
        secondary=article_categories,
        back_populates="articles",
    )
