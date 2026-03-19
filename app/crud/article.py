"""CRUD operations for Article."""

from sqlalchemy.orm import Session

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create a new article in the database.

    Args:
        db: Synchronous SQLAlchemy session.
        data: Validated article creation payload.

    Returns:
        The newly created Article instance.
    """
    article = Article(**data.model_dump())
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Article | None:
    """Retrieve a single article by primary key.

    Args:
        db: Synchronous SQLAlchemy session.
        article_id: ID of the article to retrieve.

    Returns:
        The Article if found, else None.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(db: Session, skip: int = 0, limit: int = 20) -> tuple[list[Article], int]:
    """Retrieve a paginated list of articles and total count.

    Args:
        db: Synchronous SQLAlchemy session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.

    Returns:
        A tuple of (list of Article instances, total count).
    """
    total = db.query(Article).count()
    items = db.query(Article).offset(skip).limit(limit).all()
    return items, total


def update_article(db: Session, article_id: int, data: ArticleUpdate) -> Article | None:
    """Update an existing article with the provided fields.

    Args:
        db: Synchronous SQLAlchemy session.
        article_id: ID of the article to update.
        data: Validated article update payload (only set fields are applied).

    Returns:
        The updated Article if found, else None.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return None

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by primary key.

    Args:
        db: Synchronous SQLAlchemy session.
        article_id: ID of the article to delete.

    Returns:
        True if the article was deleted, False if not found.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return False

    db.delete(article)
    db.commit()
    return True
