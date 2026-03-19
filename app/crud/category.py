"""CRUD operations for Category model."""

import re
import unicodedata

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def _generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a category name.

    Args:
        name: The category name to convert to a slug.

    Returns:
        A lowercase, hyphen-separated slug string.
    """
    # Normalize unicode characters to ASCII
    normalized = unicodedata.normalize("NFKD", name)
    ascii_str = normalized.encode("ascii", "ignore").decode("ascii")
    # Lowercase
    lower = ascii_str.lower()
    # Replace any non-alphanumeric character with a hyphen
    slug = re.sub(r"[^a-z0-9]+", "-", lower)
    # Strip leading/trailing hyphens
    slug = slug.strip("-")
    return slug


def create_category(db: Session, data: CategoryCreate) -> Category:
    """Create a new category with an auto-generated slug.

    Args:
        db: The database session.
        data: The category creation data.

    Returns:
        The newly created Category instance.
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
    """Retrieve a single category by ID.

    Args:
        db: The database session.
        category_id: The primary key of the category.

    Returns:
        The Category instance, or None if not found.
    """
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 50) -> list[Category]:
    """Retrieve a paginated list of categories.

    Args:
        db: The database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A list of Category instances.
    """
    return db.query(Category).offset(skip).limit(limit).all()


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category | None:
    """Update an existing category.

    Args:
        db: The database session.
        category_id: The primary key of the category to update.
        data: The update data (all fields optional).

    Returns:
        The updated Category instance, or None if not found.
    """
    category = get_category(db, category_id)
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
    """Delete a category by ID.

    Args:
        db: The database session.
        category_id: The primary key of the category to delete.

    Returns:
        True if the category was deleted, False if not found.
    """
    category = get_category(db, category_id)
    if category is None:
        return False

    db.delete(category)
    db.commit()
    return True
