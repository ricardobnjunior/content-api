"""REST API endpoints for article management."""

from typing import Optional

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.crud.article import (
    create_article,
    delete_article,
    get_article,
    get_articles,
    update_article,
)
from app.database import get_db
from app.models.article import ArticleStatus
from app.schemas.article import ArticleCreate, ArticleList, ArticleResponse, ArticleUpdate

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article_endpoint(
    data: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article."""
    return create_article(db, data)


@router.get("/", response_model=ArticleList)
def list_articles_endpoint(
    skip: int = 0,
    limit: int = 20,
    status: Optional[ArticleStatus] = Query(None),
    db: Session = Depends(get_db),
) -> ArticleList:
    """Retrieve a paginated list of articles."""
    total, items = get_articles(db, skip=skip, limit=limit, status=status)
    return ArticleList(total=total, items=items)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Retrieve an article by ID."""
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found.",
        )
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Update an existing article."""
    article = update_article(db, article_id, data)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found.",
        )
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete an article by ID."""
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found.",
        )
