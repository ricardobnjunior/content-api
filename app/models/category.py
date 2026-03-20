"""Category database model."""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.article import article_categories


class Category(Base):
    """Category model for classifying articles.

    Attributes:
        id: Primary key.
        name: Unique category name.
        created_at: Timestamp of creation.
        articles: Related articles.
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    articles = relationship(
        "Article", secondary=article_categories, back_populates="categories"
    )
