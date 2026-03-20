"""REST API endpoints for articles, including image upload/delete."""

import os
import shutil

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
from app.schemas.article import ArticleCreate, ArticleList, ArticleResponse, ArticleUpdate, PaginationMeta
from app.schemas.image import ImageResponse

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticleList)
def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    search: str | None = Query(None),
    category_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> ArticleList:
    """List articles with optional filters and pagination.

    Args:
        page: Page number (1-indexed).
        per_page: Number of items per page.
        status: Filter by publication status.
        search: Search term for title or content.
        category_id: Filter by category ID.
        db: Database session.

    Returns:
        Paginated list of articles with metadata.
    """
    skip = (page - 1) * per_page
    articles, total = get_articles(
        db,
        skip=skip,
        limit=per_page,
        status=status,
        search=search,
        category_id=category_id,
    )
    pages = max(1, (total + per_page - 1) // per_page)
    return ArticleList(
        items=articles,
        meta=PaginationMeta(total=total, page=page, per_page=per_page, pages=pages),
    )


@router.post("", response_model=ArticleResponse, status_code=201)
def create_new_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article.

    Args:
        article_data: Article creation payload.
        db: Database session.

    Returns:
        The newly created article.
    """
    return create_article(db, article_data)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_single_article(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Retrieve a single article by ID.

    Args:
        article_id: Article primary key.
        db: Database session.

    Returns:
        Article data.

    Raises:
        HTTPException: 404 if article not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_existing_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Update an existing article.

    Args:
        article_id: Article primary key.
        article_data: Partial update payload.
        db: Database session.

    Returns:
        Updated article data.

    Raises:
        HTTPException: 404 if article not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return update_article(db, article, article_data)


@router.delete("/{article_id}", status_code=204)
def delete_existing_article(
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

    Validates that the uploaded file is an image, saves it to disk, and updates
    the article's ``image_url`` field.

    Args:
        article_id: Article primary key.
        file: Uploaded image file (multipart/form-data).
        db: Database session.

    Returns:
        ImageResponse with filename, URL, and file size.

    Raises:
        HTTPException: 404 if article not found.
        HTTPException: 400 if the uploaded file is not an image.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)

    safe_filename = f"{article_id}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    image_url = f"/uploads/{safe_filename}"

    # Update article image_url
    article.image_url = image_url
    db.commit()
    db.refresh(article)

    return ImageResponse(filename=safe_filename, url=image_url, size=file_size)


@router.delete("/{article_id}/image", status_code=204)
def delete_article_image(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete the image associated with an article.

    Removes the image file from disk (if it exists) and clears the article's
    ``image_url`` field.

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
        # Derive filename from stored URL: /uploads/{filename}
        stored_filename = article.image_url.lstrip("/uploads/")
        # More robust: take the basename of the URL path
        stored_filename = os.path.basename(article.image_url)
        file_path = os.path.join(settings.upload_dir, stored_filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    article.image_url = None
    db.commit()
