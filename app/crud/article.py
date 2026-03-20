"""CRUD operations for Article model."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.article import Article, ArticleStatus, article_categories


def create_article(db: Session, data: dict) -> Article:
    """Create a new article in the database.

    Args:
        db: Database session.
        data: Dictionary with article fields. May include ``category_ids`` list.

    Returns:
        The newly created Article instance.
    """
    category_ids = data.pop("category_ids", [])
    article = Article(**data)
    db.add(article)
    db.flush()

    if category_ids:
        from app.models.category import Category

        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Article | None:
    """Retrieve a single article by its primary key.

    Args:
        db: Database session.
        article_id: Primary key of the article.

    Returns:
        The Article instance if found, otherwise None.
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
        db: Database session.
        page: 1-based page number.
        per_page: Number of items per page.
        search: Optional substring to match against title or body (case-insensitive).
        status: Optional exact status filter.
        author: Optional exact author filter.
        category_id: Optional category filter; returns articles belonging to this category.

    Returns:
        A tuple of ``(articles, total_count)`` where ``total_count`` is the
        count of matching records before pagination is applied.
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
        ).filter(
            article_categories.c.category_id == category_id
        ).distinct()

    total = query.count()
    offset = (page - 1) * per_page
    articles = query.offset(offset).limit(per_page).all()

    return articles, total


def update_article(db: Session, article_id: int, data: dict) -> Article | None:
    """Update an existing article.

    Args:
        db: Database session.
        article_id: Primary key of the article to update.
        data: Dictionary of fields to update. May include ``category_ids`` list.

    Returns:
        The updated Article instance, or None if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return None

    category_ids = data.pop("category_ids", None)

    for key, value in data.items():
        setattr(article, key, value)

    if category_ids is not None:
        from app.models.category import Category

        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by its primary key.

    Args:
        db: Database session.
        article_id: Primary key of the article to delete.

    Returns:
        True if the article was deleted, False if it was not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return False

    db.delete(article)
    db.commit()
    return True
