"""Category ORM model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.article import article_categories


class Category(Base):
    """Category database model."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)

    articles = relationship(
        "Article", secondary=article_categories, back_populates="categories"
    )
