"""Pydantic response models for statistics endpoints."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class CategoryStat(BaseModel):
    """Statistics for a single category."""

    category_id: int
    category_name: str
    article_count: int


class LatestArticle(BaseModel):
    """Summary of the most recently created article."""

    id: int
    title: str
    created_at: datetime


class StatsResponse(BaseModel):
    """Response model for the general statistics endpoint."""

    total_articles: int
    by_status: Dict[str, int]
    by_category: List[CategoryStat]
    total_categories: int
    latest_article: Optional[LatestArticle]


class TimelineEntry(BaseModel):
    """A single entry in the creation timeline, grouped by month."""

    month: str
    count: int


class TimelineResponse(BaseModel):
    """Response model for the timeline endpoint."""

    timeline: List[TimelineEntry]
