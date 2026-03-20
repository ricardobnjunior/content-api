"""CRUD operations for Article and Category models."""

import math
from typing import Optional

from sqlalchemy.orm import Session

from app.models.article import Article, Category
from app.schemas.article import ArticleCreate, ArticleUpdate


def get_article(db: Session, article_id: int) -> Optional[Article]:
    """Retrieve a single article by ID.

    Args:
        db: Database session.
        article_id: Primary key of the article.

    Returns:
        Article instance or None if not found.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session,
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
) -> dict:
    """Retrieve a paginated, filtered list of articles.

    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        status: Filter by publication status.
        search: Search string matched against title and content.
        category_id: Filter by category ID.

    Returns:
        Dictionary with keys ``items`` (list of Article) and ``meta`` (pagination info).
    """
    query = db.query(Article)

    if status:
        query = query.filter(Article.status == status)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Article.title.ilike(search_term) | Article.content.ilike(search_term)
        )

    if category_id:
        query = query.filter(Article.categories.any(Category.id == category_id))

    total = query.count()
    pages = math.ceil(total / per_page) if per_page > 0 else 0
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": items,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        },
    }


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create a new article.

    Args:
        db: Database session.
        data: Validated article creation payload.

    Returns:
        Newly created Article instance.
    """
    category_ids = data.category_ids or []
    article = Article(
        title=data.title,
        content=data.content,
        status=data.status,
    )

    if category_ids:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        article.categories = categories

    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def update_article(db: Session, article: Article, data: ArticleUpdate) -> Article:
    """Update an existing article.

    Only fields explicitly set in ``data`` are applied. Handles ``image_url``
    updates (including clearing the value to ``None``).

    Args:
        db: Database session.
        article: Existing Article ORM instance.
        data: Validated article update payload.

    Returns:
        Updated Article instance.
    """
    update_data = data.model_dump(exclude_unset=True)

    # Handle category relationship separately
    if "category_ids" in update_data:
        category_ids = update_data.pop("category_ids")
        if category_ids is not None:
            categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
            article.categories = categories
        else:
            article.categories = []

    # Apply all remaining scalar fields (including image_url)
    for field, value in update_data.items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article: Article) -> None:
    """Delete an article from the database.

    Args:
        db: Database session.
        article: Article ORM instance to delete.
    """
    db.delete(article)
    db.commit()
