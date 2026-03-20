"""CRUD operations for the Article model."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.article import Article, ArticleStatus, article_categories


def create_article(db: Session, data: dict) -> Article:
    """Create a new article.

    Args:
        db: SQLAlchemy database session.
        data: Dictionary with article fields. May include ``category_ids``
              (list of ints) to associate categories.

    Returns:
        The newly created :class:`Article` instance.
    """
    from app.models.category import Category

    category_ids: list[int] = data.pop("category_ids", [])
    article = Article(**data)
    if category_ids:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        article.categories = categories
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Article | None:
    """Retrieve a single article by primary key.

    Args:
        db: SQLAlchemy database session.
        article_id: Primary key of the article to retrieve.

    Returns:
        The :class:`Article` instance or ``None`` if not found.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    status: ArticleStatus | None = None,
    author: str | None = None,
    category_id: int | None = None,
) -> tuple[list[Article], int]:
    """Retrieve a paginated, filtered list of articles.

    Args:
        db: SQLAlchemy database session.
        page: Page number (1-indexed).
        per_page: Number of articles per page.
        search: Optional substring to search in ``title`` or ``body``
                (case-insensitive).
        status: Optional exact status filter.
        author: Optional exact author filter.
        category_id: Optional category ID to filter articles by membership.

    Returns:
        A tuple of ``(articles, total)`` where ``articles`` is the list for
        the requested page and ``total`` is the count before pagination.
    """
    query = db.query(Article)

    if search is not None:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(pattern),
                Article.body.ilike(pattern),
            )
        )

    if status is not None:
        query = query.filter(Article.status == status)

    if author is not None:
        query = query.filter(Article.author == author)

    if category_id is not None:
        query = query.join(
            article_categories,
            Article.id == article_categories.c.article_id,
        ).filter(article_categories.c.category_id == category_id)

    total: int = query.count()

    offset = (page - 1) * per_page
    articles: list[Article] = query.offset(offset).limit(per_page).all()

    return articles, total


def update_article(db: Session, article_id: int, data: dict) -> Article | None:
    """Update an existing article.

    Args:
        db: SQLAlchemy database session.
        article_id: Primary key of the article to update.
        data: Dictionary of fields to update. May include ``category_ids``.

    Returns:
        The updated :class:`Article` instance, or ``None`` if not found.
    """
    from app.models.category import Category

    article = get_article(db, article_id)
    if article is None:
        return None

    category_ids: list[int] | None = data.pop("category_ids", None)
    for key, value in data.items():
        setattr(article, key, value)

    if category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by primary key.

    Args:
        db: SQLAlchemy database session.
        article_id: Primary key of the article to delete.

    Returns:
        ``True`` if the article was deleted, ``False`` if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return False
    db.delete(article)
    db.commit()
    return True
