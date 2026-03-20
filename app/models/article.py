"""Article ORM model."""

from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.database import Base


class ArticleCategory(Base):
    """Association table between articles and categories."""

    __tablename__ = "article_categories"

    article_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, primary_key=True)


class Article(Base):
    """Article database model.

    Attributes:
        id: Primary key.
        title: Article title.
        content: Article body content.
        status: Publication status (draft/published).
        image_url: Optional URL to the article's uploaded image.
        created_at: Timestamp of creation.
        updated_at: Timestamp of last update.
    """

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    status = Column(String(50), default="draft", nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
