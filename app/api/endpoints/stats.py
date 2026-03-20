"""Statistics and analytics endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.models.category import Category, article_categories
from app.schemas.stats import (
    CategoryStat,
    LatestArticle,
    StatsResponse,
    TimelineEntry,
    TimelineResponse,
)

router = APIRouter()


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)) -> StatsResponse:
    """Return aggregated statistics about articles and categories.

    Args:
        db: SQLAlchemy database session.

    Returns:
        StatsResponse containing total counts, status breakdown,
        category breakdown, and latest article info.
    """
    # Total article count
    total_articles: int = db.query(func.count(Article.id)).scalar() or 0

    # Breakdown by status
    status_rows = (
        db.query(Article.status, func.count(Article.id))
        .group_by(Article.status)
        .all()
    )
    by_status = {row[0]: row[1] for row in status_rows}

    # Breakdown by category (join article_categories with categories)
    category_rows = (
        db.query(
            Category.id,
            Category.name,
            func.count(article_categories.c.article_id).label("article_count"),
        )
        .join(article_categories, Category.id == article_categories.c.category_id)
        .group_by(Category.id, Category.name)
        .all()
    )
    by_category: List[CategoryStat] = [
        CategoryStat(
            category_id=row[0],
            category_name=row[1],
            article_count=row[2],
        )
        for row in category_rows
    ]

    # Total category count
    total_categories: int = db.query(func.count(Category.id)).scalar() or 0

    # Latest article
    latest_article_orm = (
        db.query(Article).order_by(Article.created_at.desc()).first()
    )
    latest_article = (
        LatestArticle(
            id=latest_article_orm.id,
            title=latest_article_orm.title,
            created_at=latest_article_orm.created_at,
        )
        if latest_article_orm is not None
        else None
    )

    return StatsResponse(
        total_articles=total_articles,
        by_status=by_status,
        by_category=by_category,
        total_categories=total_categories,
        latest_article=latest_article,
    )


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(db: Session = Depends(get_db)) -> TimelineResponse:
    """Return article creation counts grouped by month.

    Args:
        db: SQLAlchemy database session.

    Returns:
        TimelineResponse with a list of month/count entries in
        chronological order.
    """
    month_col = func.strftime("%Y-%m", Article.created_at).label("month")
    rows = (
        db.query(month_col, func.count(Article.id).label("count"))
        .group_by(month_col)
        .order_by(month_col)
        .all()
    )
    timeline: List[TimelineEntry] = [
        TimelineEntry(month=row[0], count=row[1]) for row in rows
    ]
    return TimelineResponse(timeline=timeline)
