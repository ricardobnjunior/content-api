"""REST endpoints for Article resources."""

import math

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
from app.models.article import ArticleStatus
from app.schemas.article import (
    ArticleCreate,
    ArticleList,
    ArticleResponse,
    ArticleUpdate,
    PaginationMeta,
)

router = APIRouter()


@router.get("/", response_model=ArticleList)
def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    status: ArticleStatus | None = Query(None),
    author: str | None = Query(None),
    category_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> ArticleList:
    """List articles with optional search, filtering, and pagination.

    Args:
        page: Page number (1-based).
        per_page: Number of articles per page (1-100).
        search: Substring to search in title or body (case-insensitive).
        status: Filter by article status (draft or published).
        author: Filter by exact author name.
        category_id: Filter articles belonging to this category ID.
        db: Database session.

    Returns:
        Paginated list of articles with pagination metadata.
    """
    articles, total = get_articles(
        db=db,
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        author=author,
        category_id=category_id,
    )

    pages = math.ceil(total / per_page) if total > 0 else 0

    return ArticleList(
        items=articles,
        meta=PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article_endpoint(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article.

    Args:
        payload: Article creation data.
        db: Database session.

    Returns:
        The newly created article.
    """
    data = payload.model_dump()
    article = create_article(db, data)
    return article


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Retrieve a single article by ID.

    Args:
        article_id: Primary key of the article.
        db: Database session.

    Returns:
        The article if found.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found",
        )
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Update an existing article.

    Args:
        article_id: Primary key of the article.
        payload: Fields to update (only provided fields are changed).
        db: Database session.

    Returns:
        The updated article.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    data = payload.model_dump(exclude_unset=True)
    article = update_article(db, article_id, data)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found",
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
        db: Database session.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found",
        )
