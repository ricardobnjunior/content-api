"""CRUD operations for articles."""

from sqlalchemy.orm import Session

from app.models.article import Article, ArticleStatus
from app.models.category import Category
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create a new article.

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
    db.flush()  # Flush to get the article ID before assigning categories

    if data.category_ids:
        categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
        article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Article | None:
    """Retrieve an article by its ID.

    Args:
        db: Database session.
        article_id: The ID of the article to retrieve.

    Returns:
        The Article instance if found, otherwise None.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: ArticleStatus | None = None,
) -> tuple[int, list[Article]]:
    """Retrieve a paginated list of articles.

    Args:
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        status: Optional status filter.

    Returns:
        A tuple of (total count, list of Article instances).
    """
    query = db.query(Article)
    if status is not None:
        query = query.filter(Article.status == status)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return total, items


def update_article(db: Session, article_id: int, data: ArticleUpdate) -> Article | None:
    """Update an existing article.

    Args:
        db: Database session.
        article_id: The ID of the article to update.
        data: Article update data.

    Returns:
        The updated Article instance, or None if not found.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
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

    # Always sync categories when category_ids is provided (default is [])
    categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
    article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by its ID.

    Args:
        db: Database session.
        article_id: The ID of the article to delete.

    Returns:
        True if the article was deleted, False if not found.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return False
    db.delete(article)
    db.commit()
    return True
