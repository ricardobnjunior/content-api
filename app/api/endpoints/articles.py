"""API endpoints for articles."""

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud.article import (
    create_article,
    delete_article,
    get_article,
    get_articles,
    update_article,
)
from app.database import get_db
from app.models.article import ArticleStatus
from app.schemas.article import (
    ArticleCreate,
    ArticleList,
    ArticleResponse,
    ArticleUpdate,
    PaginationMeta,
)

router = APIRouter()


@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article_endpoint(
    article_in: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article.

    Args:
        article_in: Article creation payload.
        db: Database session dependency.

    Returns:
        The created article.
    """
    article = create_article(db=db, article_in=article_in)
    return article


@router.get("/", response_model=ArticleList)
def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[ArticleStatus] = Query(None),
    author: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
) -> ArticleList:
    """List articles with optional search, filtering, and pagination.

    Args:
        page: Page number (1-indexed, must be >= 1).
        per_page: Number of items per page (1-100).
        search: Optional search string matched against title and body.
        status: Optional status filter.
        author: Optional author filter (exact match).
        category_id: Optional category ID filter.
        db: Database session dependency.

    Returns:
        Paginated list of articles with pagination metadata.
    """
    items, total = get_articles(
        db=db,
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        author=author,
        category_id=category_id,
    )

    pages = math.ceil(total / per_page) if total > 0 else 0

    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )

    return ArticleList(items=items, meta=meta)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Get a single article by ID.

    Args:
        article_id: The ID of the article to retrieve.
        db: Database session dependency.

    Returns:
        The article data.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = get_article(db=db, article_id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int,
    article_in: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Update an existing article.

    Args:
        article_id: The ID of the article to update.
        article_in: Article update payload.
        db: Database session dependency.

    Returns:
        The updated article.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = update_article(db=db, article_id=article_id, article_in=article_in)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/{article_id}", status_code=204)
def delete_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete an article by ID.

    Args:
        article_id: The ID of the article to delete.
        db: Database session dependency.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = delete_article(db=db, article_id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
