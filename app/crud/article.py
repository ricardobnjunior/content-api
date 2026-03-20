"""CRUD operations for the Article model using a sync SQLAlchemy Session."""

from sqlalchemy.orm import Session

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create and persist a new article.

    Args:
        db: Synchronous SQLAlchemy database session.
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
    """Retrieve a single article by primary key.

    Args:
        db: Synchronous SQLAlchemy database session.
        article_id: Primary key of the article to fetch.

    Returns:
        The Article ORM instance, or None if not found.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session, skip: int = 0, limit: int = 20
) -> tuple[list[Article], int]:
    """Retrieve a paginated list of articles and the total count.

    Args:
        db: Synchronous SQLAlchemy database session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.

    Returns:
        A tuple of (list of Article instances, total article count).
    """
    total = db.query(Article).count()
    articles = db.query(Article).offset(skip).limit(limit).all()
    return articles, total


def update_article(
    db: Session, article_id: int, data: ArticleUpdate
) -> Article | None:
    """Partially update an existing article.

    Args:
        db: Synchronous SQLAlchemy database session.
        article_id: Primary key of the article to update.
        data: Validated partial update payload (None fields are ignored).

    Returns:
        The updated Article ORM instance, or None if not found.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by primary key.

    Args:
        db: Synchronous SQLAlchemy database session.
        article_id: Primary key of the article to delete.

    Returns:
        True if the article was deleted, False if not found.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return False

    db.delete(article)
    db.commit()
    return True
