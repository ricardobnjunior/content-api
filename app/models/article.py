"""Article ORM model."""

import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class ArticleStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class Article(Base):
    """Article database model."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    status = Column(Enum(ArticleStatus), nullable=False, default=ArticleStatus.draft)
    author = Column(String, nullable=False)

    categories = relationship(
        "Category", secondary=article_categories, back_populates="articles"
    )
