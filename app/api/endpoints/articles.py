"""Articles endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud.article import get_article, get_articles, create_article
from app.database import get_db

router = APIRouter()


class ArticleCreate(BaseModel):
    title: str
    content: Optional[str] = None
    status: str = "draft"


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ArticleResponse])
def list_articles(db: Session = Depends(get_db)):
    """List all articles."""
    return get_articles(db)


@router.get("/{article_id}", response_model=ArticleResponse)
def read_article(article_id: int, db: Session = Depends(get_db)):
    """Get a single article."""
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/", response_model=ArticleResponse, status_code=201)
def create(article: ArticleCreate, db: Session = Depends(get_db)):
    """Create an article."""
    return create_article(db, title=article.title, content=article.content, status=article.status)
