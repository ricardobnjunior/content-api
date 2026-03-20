"""REST endpoints for the Category resource."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter()


@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryResponse]:
    """List all categories."""
    return db.query(Category).all()


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category_endpoint(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Create a new category."""
    cat = Category(name=payload.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Retrieve a single category by ID."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat
