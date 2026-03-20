"""CRUD operations for Category."""

import re
import unicodedata

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def _generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a category name.

    Args:
        name: The category name to convert.

    Returns:
        A lowercase, hyphen-separated slug string.
    """
    # Normalize unicode characters to ASCII equivalents
    normalized = unicodedata.normalize("NFKD", name)
    ascii_str = normalized.encode("ascii", "ignore").decode("ascii")
    # Lowercase and replace non-alphanumeric chars with hyphens
    slug = re.sub(r"[^\w\s-]", "", ascii_str).strip().lower()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug


def create_category(db: Session, data: CategoryCreate) -> Category:
    """Create a new category with an auto-generated slug.

    Args:
        db: SQLAlchemy database session.
        data: Category creation data.

    Returns:
        The newly created Category instance.

    Raises:
        IntegrityError: If a category with the same name or slug already exists.
    """
    slug = _generate_slug(data.name)
    category = Category(
        name=data.name,
        slug=slug,
        description=data.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category(db: Session, category_id: int) -> Category | None:
    """Retrieve a category by its ID.

    Args:
        db: SQLAlchemy database session.
        category_id: The ID of the category to retrieve.

    Returns:
        The Category instance if found, else None.
    """
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 50) -> list[Category]:
    """Retrieve a list of categories with pagination.

    Args:
        db: SQLAlchemy database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A list of Category instances.
    """
    return db.query(Category).offset(skip).limit(limit).all()


def update_category(
    db: Session, category_id: int, data: CategoryUpdate
) -> Category | None:
    """Update an existing category.

    Args:
        db: SQLAlchemy database session.
        category_id: The ID of the category to update.
        data: Category update data.

    Returns:
        The updated Category instance if found, else None.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        return None

    if data.name is not None:
        category.name = data.name
        category.slug = _generate_slug(data.name)

    if data.description is not None:
        category.description = data.description

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category by its ID.

    Args:
        db: SQLAlchemy database session.
        category_id: The ID of the category to delete.

    Returns:
        True if the category was deleted, False if not found.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        return False
    db.delete(category)
    db.commit()
    return True
