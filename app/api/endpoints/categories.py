"""REST API endpoints for categories."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryResponse]:
    """List all categories.

    Args:
        db: Database session.

    Returns:
        List of all categories.
    """
    return db.query(Category).all()


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Create a new category.

    Args:
        category_data: Category creation payload.
        db: Database session.

    Returns:
        The newly created category.

    Raises:
        HTTPException: 400 if category name already exists.
    """
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = Category(name=category_data.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryResponse:
    """Retrieve a single category by ID.

    Args:
        category_id: Category primary key.
        db: Database session.

    Returns:
        Category data.

    Raises:
        HTTPException: 404 if category not found.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a category.

    Args:
        category_id: Category primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if category not found.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
