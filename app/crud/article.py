"""Article CRUD operations."""

from sqlalchemy.orm import Session

from app.models.article import Article


def get_article(db: Session, article_id: int):
    """Get a single article by ID."""
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(db: Session, skip: int = 0, limit: int = 100):
    """Get multiple articles."""
    return db.query(Article).offset(skip).limit(limit).all()
