"""REST endpoints for Article CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.article import (
    create_article,
    delete_article,
    get_article,
    get_articles,
    update_article,
)
from app.database import get_db
from app.schemas.article import ArticleCreate, ArticleList, ArticleResponse, ArticleUpdate

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article_endpoint(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article.

    Args:
        payload: Validated article creation data.
        db: Injected synchronous database session.

    Returns:
        The created article as an ArticleResponse.
    """
    return create_article(db, payload)


@router.get("", response_model=ArticleList)
def list_articles_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> ArticleList:
    """List articles with optional pagination.

    Args:
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.
        db: Injected synchronous database session.

    Returns:
        An ArticleList containing items and total count.
    """
    articles, total = get_articles(db, skip=skip, limit=limit)
    return ArticleList(items=articles, total=total)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Retrieve a single article by ID.

    Args:
        article_id: Primary key of the article to fetch.
        db: Injected synchronous database session.

    Returns:
        The article as an ArticleResponse.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id {article_id} not found",
        )
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Update an existing article (partial update supported).

    Args:
        article_id: Primary key of the article to update.
        payload: Partial update payload; unset fields are ignored.
        db: Injected synchronous database session.

    Returns:
        The updated article as an ArticleResponse.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    article = update_article(db, article_id, payload)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id {article_id} not found",
        )
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete an article by ID.

    Args:
        article_id: Primary key of the article to delete.
        db: Injected synchronous database session.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id {article_id} not found",
        )
