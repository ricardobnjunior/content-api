"""CRUD operations for Article model."""

from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.category import Category
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create a new article, optionally linked to categories.

    Args:
        db: The database session.
        data: The article creation data including optional category_ids.

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
    db.flush()  # Flush to get the article ID before assigning categories

    if data.category_ids:
        categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
        article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Article | None:
    """Retrieve a single article by ID.

    Args:
        db: The database session.
        article_id: The primary key of the article.

    Returns:
        The Article instance, or None if not found.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(db: Session, skip: int = 0, limit: int = 20) -> tuple[int, list[Article]]:
    """Retrieve a paginated list of articles.

    Args:
        db: The database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A tuple of (total_count, list_of_articles).
    """
    query = db.query(Article)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return total, items


def update_article(db: Session, article_id: int, data: ArticleUpdate) -> Article | None:
    """Update an existing article.

    Args:
        db: The database session.
        article_id: The primary key of the article to update.
        data: The update data (all fields optional).

    Returns:
        The updated Article instance, or None if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return None

    if data.title is not None:
        article.title = data.title
    if data.body is not None:
        article.body = data.body
    if data.author is not None:
        article.author = data.author
    if data.status is not None:
        article.status = data.status

    # Always update categories (empty list clears them)
    categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
    article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by ID.

    Args:
        db: The database session.
        article_id: The primary key of the article to delete.

    Returns:
        True if the article was deleted, False if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return False

    db.delete(article)
    db.commit()
    return True
