"""CRUD operations for Article resources."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create a new article in the database.

    Args:
        db: SQLAlchemy database session.
        data: Validated article creation payload.

    Returns:
        The newly created Article ORM instance.
    """
    article = Article(
        title=data.title,
        body=data.body,
        author=data.author,
        status=data.status,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Article | None:
    """Fetch a single article by its primary key.

    Args:
        db: SQLAlchemy database session.
        article_id: Primary key of the article to retrieve.

    Returns:
        The Article ORM instance, or None if not found.
    """
    return db.get(Article, article_id)


def get_articles(
    db: Session, skip: int = 0, limit: int = 20
) -> tuple[list[Article], int]:
    """Fetch a paginated list of articles.

    Args:
        db: SQLAlchemy database session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.

    Returns:
        A tuple of (list of Article instances, total count).
    """
    total: int = db.execute(select(func.count()).select_from(Article)).scalar_one()
    articles = db.execute(
        select(Article).order_by(Article.id).offset(skip).limit(limit)
    ).scalars().all()
    return list(articles), total


def update_article(
    db: Session, article_id: int, data: ArticleUpdate
) -> Article | None:
    """Update an existing article with the provided fields.

    Only fields explicitly set (non-None) in ``data`` are applied.

    Args:
        db: SQLAlchemy database session.
        article_id: Primary key of the article to update.
        data: Validated partial or full update payload.

    Returns:
        The updated Article ORM instance, or None if not found.
    """
    article = db.get(Article, article_id)
    if article is None:
        return None

    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by its primary key.

    Args:
        db: SQLAlchemy database session.
        article_id: Primary key of the article to delete.

    Returns:
        True if the article was deleted, False if it was not found.
    """
    article = db.get(Article, article_id)
    if article is None:
        return False

    db.delete(article)
    db.commit()
    return True
