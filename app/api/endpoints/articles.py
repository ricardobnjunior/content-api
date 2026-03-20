"""Articles API endpoints."""

import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.article import (
    create_article,
    delete_article,
    get_article,
    get_articles,
    update_article,
)
from app.database import get_db

router = APIRouter(prefix="/articles", tags=["articles"])


class ArticleResponse(BaseModel):
    """Response model for article data."""

    id: int
    title: str
    content: Optional[str] = None
    image_path: Optional[str] = None

    model_config = {"from_attributes": True}


class ArticleCreate(BaseModel):
    """Request model for creating an article."""

    title: str
    content: Optional[str] = None


class ArticleUpdate(BaseModel):
    """Request model for updating an article."""

    title: Optional[str] = None
    content: Optional[str] = None


@router.get("/", response_model=List[ArticleResponse])
def list_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all articles."""
    return get_articles(db, skip=skip, limit=limit)


@router.get("/{article_id}", response_model=ArticleResponse)
def read_article(article_id: int, db: Session = Depends(get_db)):
    """Get a single article by ID."""
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article_endpoint(article: ArticleCreate, db: Session = Depends(get_db)):
    """Create a new article."""
    return create_article(db, title=article.title, content=article.content)


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(article_id: int, article: ArticleUpdate, db: Session = Depends(get_db)):
    """Update an existing article."""
    updated = update_article(db, article_id, **article.model_dump(exclude_none=True))
    if updated is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated


@router.delete("/{article_id}", status_code=204)
def delete_article_endpoint(article_id: int, db: Session = Depends(get_db)):
    """Delete an article."""
    if not delete_article(db, article_id):
        raise HTTPException(status_code=404, detail="Article not found")


@router.post("/{article_id}/image", response_model=ArticleResponse)
async def upload_article_image(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload an image for an article."""
    import aiofiles

    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "image.jpg")[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(settings.upload_dir, filename)

    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    updated = update_article(db, article_id, image_path=filepath)
    return updated
