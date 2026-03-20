"""REST API endpoints for articles."""

import os
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.crud.article import (
    create_article,
    delete_article,
    get_article,
    get_articles,
    update_article,
)
from app.database import get_db
from app.schemas.article import ArticleCreate, ArticleList, ArticleResponse, ArticleUpdate
from app.schemas.image import ImageResponse

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/", response_model=ArticleList)
def list_articles(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
) -> ArticleList:
    """List articles with optional filtering and pagination.

    Args:
        page: Page number (1-based).
        per_page: Number of results per page.
        status: Filter by publication status.
        search: Full-text search term.
        category_id: Filter by category ID.
        db: Database session.

    Returns:
        Paginated list of articles.
    """
    result = get_articles(
        db,
        page=page,
        per_page=per_page,
        status=status,
        search=search,
        category_id=category_id,
    )
    return ArticleList(
        items=result["items"],
        meta=result["meta"],
    )


@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article_endpoint(
    article_in: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article.

    Args:
        article_in: Article creation payload.
        db: Database session.

    Returns:
        The newly created article.
    """
    return create_article(db, article_in)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Retrieve a single article by ID.

    Args:
        article_id: Article primary key.
        db: Database session.

    Returns:
        The requested article.

    Raises:
        HTTPException: 404 if article not found.
    """
    article = get_article(db, article_id)
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
        article_id: Article primary key.
        article_in: Article update payload.
        db: Database session.

    Returns:
        The updated article.

    Raises:
        HTTPException: 404 if article not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return update_article(db, article, article_in)


@router.delete("/{article_id}", status_code=204)
def delete_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete an article.

    Args:
        article_id: Article primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if article not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    delete_article(db, article)


@router.post("/{article_id}/image", response_model=ImageResponse, status_code=201)
def upload_article_image(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ImageResponse:
    """Upload an image for an article.

    Validates the article exists and the uploaded file is an image.
    Saves the file to disk and updates the article's image_url field.

    Args:
        article_id: Article primary key.
        file: Uploaded image file.
        db: Database session.

    Returns:
        ImageResponse with filename, url, and size.

    Raises:
        HTTPException: 404 if article not found.
        HTTPException: 400 if file is not an image.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)

    original_filename = file.filename or "upload"
    filename = f"{article_id}_{original_filename}"
    filepath = os.path.join(settings.upload_dir, filename)

    file_content = file.file.read()
    file_size = len(file_content)

    with open(filepath, "wb") as f:
        f.write(file_content)

    image_url = f"/uploads/{filename}"
    article.image_url = image_url
    db.commit()
    db.refresh(article)

    return ImageResponse(filename=filename, url=image_url, size=file_size)


@router.delete("/{article_id}/image", status_code=204)
def delete_article_image(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete the image associated with an article.

    Removes the file from disk and clears the article's image_url field.

    Args:
        article_id: Article primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if article not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.image_url:
        settings = get_settings()
        filename = os.path.basename(article.image_url)
        filepath = os.path.join(settings.upload_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    article.image_url = None
    db.commit()
