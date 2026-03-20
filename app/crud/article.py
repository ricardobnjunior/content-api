"""CRUD operations for articles."""

from sqlalchemy.orm import Session

from app.models.article import Article


def get_article(db: Session, article_id: int):
    """Get a single article by ID."""
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(db: Session, skip: int = 0, limit: int = 100):
    """Get all articles."""
    return db.query(Article).offset(skip).limit(limit).all()


def create_article(db: Session, title: str, content: str = None, status: str = "draft"):
    """Create a new article."""
    article = Article(title=title, content=content, status=status)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article
