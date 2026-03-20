"""Categories API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud.category import (
    create_category,
    delete_category,
    get_categories,
    get_category,
    get_category_by_name,
)
from app.database import get_db

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryResponse(BaseModel):
    """Response model for category data."""

    id: int
    name: str

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    """Request model for creating a category."""

    name: str


@router.get("/", response_model=List[CategoryResponse])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all categories."""
    return get_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """Get a single category by ID."""
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category_endpoint(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    existing = get_category_by_name(db, category.name)
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    return create_category(db, name=category.name)


@router.delete("/{category_id}", status_code=204)
def delete_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    if not delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
