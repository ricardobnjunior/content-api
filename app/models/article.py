"""Article and Category ORM models."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import relationship

from app.database import Base

# Association table for many-to-many Article <-> Category
article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class Category(Base):
    """Category model.

    Attributes:
        id: Primary key.
        name: Unique category name.
        articles: Related articles (many-to-many).
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    articles = relationship("Article", secondary=article_categories, back_populates="categories")


class Article(Base):
    """Article model.

    Attributes:
        id: Primary key.
        title: Article title.
        content: Article body text.
        status: Publication status (draft/published/archived).
        image_url: Optional URL to the article's cover image.
        created_at: Timestamp when article was created.
        updated_at: Timestamp when article was last updated.
        categories: Related categories (many-to-many).
    """

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    categories = relationship("Category", secondary=article_categories, back_populates="articles")
