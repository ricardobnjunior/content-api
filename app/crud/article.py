"""CRUD operations for articles."""

from sqlalchemy.orm import Session

from app.models.article import Article


def get_article(db: Session, article_id: int) -> Article | None:
    """Retrieve an article by ID.

    Args:
        db: Database session.
        article_id: The article's primary key.

    Returns:
        The Article instance if found, otherwise None.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(db: Session, skip: int = 0, limit: int = 100) -> list[Article]:
    """Retrieve a list of articles with pagination.

    Args:
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of Article instances.
    """
    return db.query(Article).offset(skip).limit(limit).all()


def create_article(db: Session, title: str, content: str | None = None, image_path: str | None = None) -> Article:
    """Create a new article.

    Args:
        db: Database session.
        title: Article title.
        content: Article content.
        image_path: Optional path to image.

    Returns:
        The newly created Article instance.
    """
    article = Article(title=title, content=content, image_path=image_path)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def update_article(db: Session, article_id: int, **kwargs) -> Article | None:
    """Update an existing article.

    Args:
        db: Database session.
        article_id: The article's primary key.
        **kwargs: Fields to update.

    Returns:
        The updated Article instance or None if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return None
    for key, value in kwargs.items():
        setattr(article, key, value)
    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by ID.

    Args:
        db: Database session.
        article_id: The article's primary key.

    Returns:
        True if deleted, False if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return False
    db.delete(article)
    db.commit()
    return True
