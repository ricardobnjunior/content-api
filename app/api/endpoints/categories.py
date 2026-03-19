"""REST endpoints for Category resources."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.category import (
    create_category,
    delete_category,
    get_categories,
    get_category,
    update_category,
)
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(
    data: CategoryCreate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Create a new category."""
    try:
        category = create_category(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists.",
        ) from None
    return category  # type: ignore[return-value]


@router.get("", response_model=List[CategoryResponse])
def list_categories_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> List[CategoryResponse]:
    """List all categories with optional pagination."""
    return get_categories(db, skip=skip, limit=limit)  # type: ignore[return-value]


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Retrieve a single category by ID."""
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found.",
        )
    return category  # type: ignore[return-value]


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category_endpoint(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Update an existing category."""
    category = update_category(db, category_id, data)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found.",
        )
    return category  # type: ignore[return-value]


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a category by ID."""
    deleted = delete_category(db, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found.",
        )
