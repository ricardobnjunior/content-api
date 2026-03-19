"""Category model with SQLAlchemy ORM."""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.article import article_categories


class Category(Base):
    """ORM model representing a content category."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    articles = relationship(
        "Article",
        secondary=article_categories,
        back_populates="categories",
    )
