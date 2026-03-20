"""CRUD operations for categories."""

from sqlalchemy.orm import Session

from app.models.category import Category


def get_category(db: Session, category_id: int) -> Category | None:
    """Retrieve a category by ID.

    Args:
        db: Database session.
        category_id: The category's primary key.

    Returns:
        The Category instance if found, otherwise None.
    """
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Category | None:
    """Retrieve a category by name.

    Args:
        db: Database session.
        name: The category name.

    Returns:
        The Category instance if found, otherwise None.
    """
    return db.query(Category).filter(Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[Category]:
    """Retrieve a list of categories with pagination.

    Args:
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of Category instances.
    """
    return db.query(Category).offset(skip).limit(limit).all()


def create_category(db: Session, name: str) -> Category:
    """Create a new category.

    Args:
        db: Database session.
        name: Category name.

    Returns:
        The newly created Category instance.
    """
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category by ID.

    Args:
        db: Database session.
        category_id: The category's primary key.

    Returns:
        True if deleted, False if not found.
    """
    category = get_category(db, category_id)
    if category is None:
        return False
    db.delete(category)
    db.commit()
    return True
