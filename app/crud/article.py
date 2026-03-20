"""CRUD operations for articles."""

import math
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.article import Article, ArticleCategory
from app.schemas.article import ArticleCreate, ArticleUpdate


def get_article(db: Session, article_id: int) -> Optional[Article]:
    """Retrieve a single article by ID.

    Args:
        db: Database session.
        article_id: Primary key of the article.

    Returns:
        The Article instance or None if not found.
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
    """Retrieve a paginated list of articles with optional filters.

    Args:
        db: Database session.
        page: Page number (1-based).
        per_page: Number of items per page.
        status: Filter by publication status.
        search: Search term for title/content.
        category_id: Filter by category ID.

    Returns:
        Dictionary with 'items' list and 'meta' pagination info.
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
        query = query.join(
            ArticleCategory,
            Article.id == ArticleCategory.article_id,
        ).filter(ArticleCategory.category_id == category_id)

    total = query.count()
    total_pages = max(1, math.ceil(total / per_page))
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()

    return {
        "items": items,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
        },
    }


def create_article(db: Session, article_in: ArticleCreate) -> Article:
    """Create a new article record.

    Args:
        db: Database session.
        article_in: Validated article creation data.

    Returns:
        The newly created Article instance.
    """
    db_article = Article(
        title=article_in.title,
        content=article_in.content,
        status=article_in.status,
    )
    db.add(db_article)
    db.flush()

    if article_in.category_ids:
        for cat_id in article_in.category_ids:
            assoc = ArticleCategory(article_id=db_article.id, category_id=cat_id)
            db.add(assoc)

    db.commit()
    db.refresh(db_article)
    return db_article


def update_article(
    db: Session,
    article: Article,
    article_in: ArticleUpdate,
    image_url: Optional[str] = None,
) -> Article:
    """Update an existing article record.

    Args:
        db: Database session.
        article: Existing Article ORM instance to update.
        article_in: Validated update data.
        image_url: Optional new image URL to set on the article.

    Returns:
        The updated Article instance.
    """
    if article_in.title is not None:
        article.title = article_in.title
    if article_in.content is not None:
        article.content = article_in.content
    if article_in.status is not None:
        article.status = article_in.status

    if image_url is not None:
        article.image_url = image_url

    if article_in.category_ids is not None:
        db.query(ArticleCategory).filter(
            ArticleCategory.article_id == article.id
        ).delete()
        for cat_id in article_in.category_ids:
            assoc = ArticleCategory(article_id=article.id, category_id=cat_id)
            db.add(assoc)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article: Article) -> None:
    """Delete an article record from the database.

    Args:
        db: Database session.
        article: Article ORM instance to delete.
    """
    db.delete(article)
    db.commit()
