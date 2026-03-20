"""CRUD operations for articles."""

from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.article import Article, ArticleStatus, article_categories
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, article_in: ArticleCreate) -> Article:
    """Create a new article.

    Args:
        db: Database session.
        article_in: Article creation schema.

    Returns:
        The created Article ORM object.
    """
    from app.models.category import Category

    article = Article(
        title=article_in.title,
        body=article_in.body,
        status=article_in.status,
        author=article_in.author,
    )
    if article_in.category_ids:
        categories = db.query(Category).filter(
            Category.id.in_(article_in.category_ids)
        ).all()
        article.categories = categories

    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Optional[Article]:
    """Get a single article by ID.

    Args:
        db: Database session.
        article_id: The ID of the article to retrieve.

    Returns:
        The Article ORM object, or None if not found.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    status: Optional[ArticleStatus] = None,
    author: Optional[str] = None,
    category_id: Optional[int] = None,
) -> tuple[list[Article], int]:
    """Get a paginated, filtered list of articles.

    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        search: Optional search string matched against title and body (case-insensitive).
        status: Optional status filter (exact match).
        author: Optional author filter (exact match).
        category_id: Optional category ID filter; returns articles belonging to this category.

    Returns:
        A tuple of (list of Article objects, total count before pagination).
    """
    query = db.query(Article)

    # Apply search filter (case-insensitive match on title OR body)
    if search is not None:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_pattern),
                Article.body.ilike(search_pattern),
            )
        )

    # Apply status filter
    if status is not None:
        query = query.filter(Article.status == status)

    # Apply author filter
    if author is not None:
        query = query.filter(Article.author == author)

    # Apply category filter via join through article_categories table
    if category_id is not None:
        query = query.join(
            article_categories,
            Article.id == article_categories.c.article_id,
        ).filter(article_categories.c.category_id == category_id)

    # Count total before pagination
    total = query.with_entities(func.count(Article.id)).scalar()

    # Apply pagination
    offset = (page - 1) * per_page
    articles = query.offset(offset).limit(per_page).all()

    return articles, total


def update_article(
    db: Session, article_id: int, article_in: ArticleUpdate
) -> Optional[Article]:
    """Update an existing article.

    Args:
        db: Database session.
        article_id: The ID of the article to update.
        article_in: Article update schema with fields to change.

    Returns:
        The updated Article ORM object, or None if not found.
    """
    from app.models.category import Category

    article = get_article(db, article_id)
    if article is None:
        return None

    update_data = article_in.model_dump(exclude_unset=True)
    category_ids = update_data.pop("category_ids", None)

    for field, value in update_data.items():
        setattr(article, field, value)

    if category_ids is not None:
        categories = db.query(Category).filter(
            Category.id.in_(category_ids)
        ).all()
        article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> Optional[Article]:
    """Delete an article by ID.

    Args:
        db: Database session.
        article_id: The ID of the article to delete.

    Returns:
        The deleted Article ORM object, or None if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return None
    db.delete(article)
    db.commit()
    return article
