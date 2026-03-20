"""Article ORM model."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import relationship

from app.database import Base

# Association table for article-category many-to-many relationship
article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class Article(Base):
    """Article database model.

    Attributes:
        id: Primary key.
        title: Article title.
        content: Article body content.
        status: Publication status (draft/published).
        image_url: Optional URL path to the article's uploaded image.
        created_at: Timestamp when the article was created.
        updated_at: Timestamp when the article was last updated.
        categories: Many-to-many relationship with Category.
    """

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    categories = relationship(
        "Category",
        secondary=article_categories,
        back_populates="articles",
    )
