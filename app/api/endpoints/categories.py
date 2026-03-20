"""REST API endpoints for category management."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

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


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(
    data: CategoryCreate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Create a new category.

    Args:
        data: Category creation payload.
        db: Database session (injected).

    Returns:
        The newly created category.

    Raises:
        HTTPException: 409 if a category with the same name already exists.
    """
    try:
        return create_category(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists.",
        ) from None


@router.get("/", response_model=list[CategoryResponse])
def list_categories_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[CategoryResponse]:
    """Retrieve a list of categories.

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        db: Database session (injected).

    Returns:
        A list of category objects.
    """
    return get_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Retrieve a category by ID.

    Args:
        category_id: The ID of the category to retrieve.
        db: Database session (injected).

    Returns:
        The category with the given ID.

    Raises:
        HTTPException: 404 if the category is not found.
    """
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found.",
        )
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category_endpoint(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Update an existing category.

    Args:
        category_id: The ID of the category to update.
        data: Category update payload.
        db: Database session (injected).

    Returns:
        The updated category.

    Raises:
        HTTPException: 404 if the category is not found.
    """
    category = update_category(db, category_id, data)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found.",
        )
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a category by ID.

    Args:
        category_id: The ID of the category to delete.
        db: Database session (injected).

    Raises:
        HTTPException: 404 if the category is not found.
    """
    deleted = delete_category(db, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found.",
        )
