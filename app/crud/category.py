"""CRUD operations for categories."""

import re

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug.

    Args:
        text: The text to convert.

    Returns:
        A lowercase, hyphenated slug string.
    """
    text = text.lower().strip()
    # Replace non-alphanumeric characters (except hyphens) with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    return text


def create_category(db: Session, data: CategoryCreate) -> Category:
    """Create a new category with auto-generated slug.

    Args:
        db: Database session.
        data: Category creation data.

    Returns:
        The newly created Category instance.
    """
    slug = _slugify(data.name)
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
        db: Database session.
        category_id: The ID of the category to retrieve.

    Returns:
        The Category instance if found, otherwise None.
    """
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 50) -> list[Category]:
    """Retrieve a list of categories with pagination.

    Args:
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A list of Category instances.
    """
    return db.query(Category).offset(skip).limit(limit).all()


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category | None:
    """Update an existing category.

    Args:
        db: Database session.
        category_id: The ID of the category to update.
        data: Category update data.

    Returns:
        The updated Category instance, or None if not found.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        return None

    if data.name is not None:
        category.name = data.name
        category.slug = _slugify(data.name)

    if data.description is not None:
        category.description = data.description

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category by its ID.

    Args:
        db: Database session.
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
