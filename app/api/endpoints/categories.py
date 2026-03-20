"""REST endpoints for the Category resource."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Category

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryCreate(BaseModel):
    """Schema for creating a category.

    Attributes:
        name: Unique category name.
    """

    name: str


class CategoryResponse(BaseModel):
    """Schema for category responses.

    Attributes:
        id: Category identifier.
        name: Category name.
    """

    id: int
    name: str

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryResponse]:
    """List all categories.

    Args:
        db: Database session.

    Returns:
        List of all categories.
    """
    return db.query(Category).all()


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)) -> CategoryResponse:
    """Create a new category.

    Args:
        data: Category creation payload.
        db: Database session.

    Returns:
        Created category data.

    Raises:
        HTTPException: 409 if a category with the same name already exists.
    """
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")
    category = Category(name=data.name)
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
        HTTPException: 404 if the category does not exist.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a category.

    Args:
        category_id: Category primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if the category does not exist.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
