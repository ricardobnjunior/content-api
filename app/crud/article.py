"""CRUD operations for Article model."""

from sqlalchemy.orm import Session

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create a new article in the database.

    Args:
        db: Database session.
        data: Article creation data.

    Returns:
        The newly created Article instance.
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
    """Retrieve a single article by ID.

    Args:
        db: Database session.
        article_id: Primary key of the article to retrieve.

    Returns:
        The Article instance if found, None otherwise.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session, skip: int = 0, limit: int = 20
) -> tuple[list[Article], int]:
    """Retrieve a paginated list of articles.

    Args:
        db: Database session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.

    Returns:
        A tuple of (list of Article instances, total count).
    """
    total = db.query(Article).count()
    articles = db.query(Article).offset(skip).limit(limit).all()
    return articles, total


def update_article(
    db: Session, article_id: int, data: ArticleUpdate
) -> Article | None:
    """Update an existing article with provided fields.

    Args:
        db: Database session.
        article_id: Primary key of the article to update.
        data: Article update data (only non-None fields are applied).

    Returns:
        The updated Article instance if found, None otherwise.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return None

    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by ID.

    Args:
        db: Database session.
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
