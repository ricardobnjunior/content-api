"""Categories API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.category import Category

router = APIRouter()


class CategorySchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str


@router.get("/", response_model=List[CategorySchema])
def list_categories(db: Session = Depends(get_db)):
    """List all categories."""
    return db.query(Category).all()


@router.get("/{category_id}", response_model=CategorySchema)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """Get a single category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategorySchema, status_code=201)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    category = Category(name=category_in.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
