"""CRUD operations for articles."""

from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.category import Category
from app.schemas.article import ArticleCreate, ArticleUpdate


def get_article(db: Session, article_id: int) -> Article | None:
    """Retrieve a single article by its primary key.

    Args:
        db: Database session.
        article_id: Primary key of the article.

    Returns:
        Article instance or None if not found.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status: str | None = None,
    search: str | None = None,
    category_id: int | None = None,
) -> tuple[list[Article], int]:
    """Retrieve a paginated list of articles with optional filters.

    Args:
        db: Database session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.
        status: Filter by publication status.
        search: Full-text search term for title or content.
        category_id: Filter by associated category ID.

    Returns:
        Tuple of (list of Article instances, total count).
    """
    query = db.query(Article)

    if status:
        query = query.filter(Article.status == status)

    if search:
        query = query.filter(
            Article.title.ilike(f"%{search}%") | Article.content.ilike(f"%{search}%")
        )

    if category_id:
        query = query.filter(Article.categories.any(Category.id == category_id))

    total = query.count()
    articles = query.offset(skip).limit(limit).all()
    return articles, total


def create_article(db: Session, article_data: ArticleCreate) -> Article:
    """Create a new article.

    Args:
        db: Database session.
        article_data: Validated article creation data.

    Returns:
        Newly created Article instance.
    """
    category_ids = article_data.category_ids
    article_dict = article_data.model_dump(exclude={"category_ids"})
    db_article = Article(**article_dict)

    if category_ids:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        db_article.categories = categories

    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def update_article(db: Session, article: Article, article_data: ArticleUpdate) -> Article:
    """Update an existing article with partial data.

    Only fields explicitly provided (non-None) in ``article_data`` are updated.
    The ``image_url`` field is handled directly on the model when present in the
    update payload.

    Args:
        db: Database session.
        article: Existing Article instance to update.
        article_data: Validated partial update data.

    Returns:
        Updated Article instance.
    """
    update_dict = article_data.model_dump(exclude_unset=True)

    # Handle category_ids separately
    category_ids = update_dict.pop("category_ids", None)
    if category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        article.categories = categories

    # Apply remaining scalar fields (including image_url if provided)
    for field, value in update_dict.items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article: Article) -> None:
    """Delete an article from the database.

    Args:
        db: Database session.
        article: Article instance to delete.
    """
    db.delete(article)
    db.commit()
