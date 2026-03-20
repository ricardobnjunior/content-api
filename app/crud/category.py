"""CRUD operations for categories."""

from sqlalchemy.orm import Session

from app.models.category import Category


def get_category(db: Session, category_id: int):
    """Get a single category by ID."""
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    """Get all categories."""
    return db.query(Category).offset(skip).limit(limit).all()


def create_category(db: Session, name: str, description: str = None):
    """Create a new category."""
    category = Category(name=name, description=description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
