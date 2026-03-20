"""Articles API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.crud.article import get_article, get_articles
from app.models.article import Article

router = APIRouter()


class ArticleSchema(BaseModel):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
    status: str = "draft"

    class Config:
        from_attributes = True


class ArticleCreate(BaseModel):
    title: str
    content: str
    status: str = "draft"
    category_id: Optional[int] = None


@router.get("/", response_model=List[ArticleSchema])
def list_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all articles."""
    return get_articles(db, skip=skip, limit=limit)


@router.get("/{article_id}", response_model=ArticleSchema)
def read_article(article_id: int, db: Session = Depends(get_db)):
    """Get a single article."""
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/", response_model=ArticleSchema, status_code=201)
def create_article(article_in: ArticleCreate, db: Session = Depends(get_db)):
    """Create a new article."""
    article = Article(
        title=article_in.title,
        content=article_in.content,
        status=article_in.status,
        category_id=article_in.category_id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article
