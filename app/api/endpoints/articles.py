"""REST endpoints for the Article resource, including image upload/delete."""

import os

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
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    search: str | None = Query(None),
    category_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> ArticleList:
    """List articles with optional filtering and pagination.

    Args:
        page: Page number (1-indexed).
        per_page: Number of items per page (1-100).
        status: Filter by publication status.
        search: Search string matched against title and content.
        category_id: Filter by category ID.
        db: Database session.

    Returns:
        Paginated article list with metadata.
    """
    result = get_articles(
        db,
        page=page,
        per_page=per_page,
        status=status,
        search=search,
        category_id=category_id,
    )
    return ArticleList(**result)


@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article_endpoint(
    data: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article.

    Args:
        data: Article creation payload.
        db: Database session.

    Returns:
        Created article data.
    """
    article = create_article(db, data)
    return article


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
        Article data.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Update an existing article.

    Args:
        article_id: Article primary key.
        data: Article update payload (all fields optional).
        db: Database session.

    Returns:
        Updated article data.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article = update_article(db, article, data)
    return article


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
        HTTPException: 404 if the article does not exist.
    """
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    delete_article(db, article)


@router.post("/{article_id}/image", response_model=ImageResponse, status_code=201)
def upload_article_image(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ImageResponse:
    """Upload a cover image for an article.

    The file is saved to ``{upload_dir}/{article_id}_{original_filename}`` and
    the article's ``image_url`` field is updated to the public path.

    Args:
        article_id: Article primary key.
        file: Uploaded image file (must have an image/* content type).
        db: Database session.

    Returns:
        ImageResponse with filename, public URL, and file size in bytes.

    Raises:
        HTTPException: 404 if the article does not exist.
        HTTPException: 400 if the uploaded file is not an image.
    """
    settings = get_settings()

    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    original_filename = file.filename or "upload"
    saved_filename = f"{article_id}_{original_filename}"
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, saved_filename)

    file_content = file.file.read()
    file_size = len(file_content)

    with open(file_path, "wb") as f:
        f.write(file_content)

    public_url = f"/uploads/{saved_filename}"
    data = ArticleUpdate(image_url=public_url)
    update_article(db, article, data)

    return ImageResponse(
        filename=saved_filename,
        url=public_url,
        size=file_size,
    )


@router.delete("/{article_id}/image", status_code=204)
def delete_article_image(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Remove the cover image from an article.

    Deletes the file from disk if it exists and clears the article's
    ``image_url`` field.

    Args:
        article_id: Article primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    settings = get_settings()

    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.image_url:
        # Derive the filename from the stored URL (/uploads/<filename>)
        filename = article.image_url.lstrip("/uploads/")
        # Use os.path.basename to be safe with any URL format
        filename = os.path.basename(article.image_url)
        file_path = os.path.join(settings.upload_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    data = ArticleUpdate(image_url=None)
    # image_url=None won't be in exclude_unset unless we force it
    article.image_url = None
    db.commit()
    db.refresh(article)
