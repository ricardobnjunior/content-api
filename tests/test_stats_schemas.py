"""Tests for stats Pydantic schemas."""

from datetime import datetime

import pytest

from app.schemas.stats import (
    CategoryStat,
    LatestArticle,
    StatsResponse,
    TimelineEntry,
    TimelineResponse,
)


class TestCategoryStat:
    """Tests for CategoryStat schema."""

    def test_happy_path(self):
        stat = CategoryStat(category_id=1, category_name="Tech", article_count=5)
        assert stat.category_id == 1
        assert stat.category_name == "Tech"
        assert stat.article_count == 5

    def test_zero_article_count(self):
        stat = CategoryStat(category_id=99, category_name="Empty", article_count=0)
        assert stat.article_count == 0

    def test_serialization(self):
        stat = CategoryStat(category_id=2, category_name="Science", article_count=10)
        data = stat.model_dump()
        assert data == {"category_id": 2, "category_name": "Science", "article_count": 10}


class TestLatestArticle:
    """Tests for LatestArticle schema."""

    def test_happy_path(self):
        dt = datetime(2026, 3, 20, 10, 0, 0)
        article = LatestArticle(id=42, title="Latest Post", created_at=dt)
        assert article.id == 42
        assert article.title == "Latest Post"
        assert article.created_at == dt

    def test_serialization(self):
        dt = datetime(2026, 1, 15, 0, 0, 0)
        article = LatestArticle(id=1, title="First", created_at=dt)
        data = article.model_dump()
        assert data["id"] == 1
        assert data["title"] == "First"
        assert data["created_at"] == dt


class TestStatsResponse:
    """Tests for StatsResponse schema."""

    def test_happy_path(self):
        dt = datetime(2026, 3, 20, 10, 0, 0)
        resp = StatsResponse(
            total_articles=42,
            by_status={"draft": 15, "published": 27},
            by_category=[
                CategoryStat(category_id=1, category_name="Tech", article_count=12)
            ],
            total_categories=5,
            latest_article=LatestArticle(id=42, title="Latest", created_at=dt),
        )
        assert resp.total_articles == 42
        assert resp.by_status["draft"] == 15
        assert resp.by_status["published"] == 27
        assert len(resp.by_category) == 1
        assert resp.total_categories == 5
        assert resp.latest_article is not None
        assert resp.latest_article.id == 42

    def test_no_latest_article(self):
        resp = StatsResponse(
            total_articles=0,
            by_status={},
            by_category=[],
            total_categories=0,
            latest_article=None,
        )
        assert resp.latest_article is None
        assert resp.total_articles == 0

    def test_empty_by_status(self):
        resp = StatsResponse(
            total_articles=0,
            by_status={},
            by_category=[],
            total_categories=0,
            latest_article=None,
        )
        assert resp.by_status == {}

    def test_multiple_categories(self):
        categories = [
            CategoryStat(category_id=i, category_name=f"Cat{i}", article_count=i * 2)
            for i in range(1, 4)
        ]
        resp = StatsResponse(
            total_articles=12,
            by_status={"published": 12},
            by_category=categories,
            total_categories=3,
            latest_article=None,
        )
        assert len(resp.by_category) == 3
        assert resp.by_category[0].category_name == "Cat1"


class TestTimelineEntry:
    """Tests for TimelineEntry schema."""

    def test_happy_path(self):
        entry = TimelineEntry(month="2026-01", count=5)
        assert entry.month == "2026-01"
        assert entry.count == 5

    def test_zero_count(self):
        entry = TimelineEntry(month="2026-02", count=0)
        assert entry.count == 0

    def test_serialization(self):
        entry = TimelineEntry(month="2026-03", count=25)
        data = entry.model_dump()
        assert data == {"month": "2026-03", "count": 25}


class TestTimelineResponse:
    """Tests for TimelineResponse schema."""

    def test_happy_path(self):
        resp = TimelineResponse(
            timeline=[
                TimelineEntry(month="2026-01", count=5),
                TimelineEntry(month="2026-02", count=12),
                TimelineEntry(month="2026-03", count=25),
            ]
        )
        assert len(resp.timeline) == 3
        assert resp.timeline[0].month == "2026-01"
        assert resp.timeline[2].count == 25

    def test_empty_timeline(self):
        resp = TimelineResponse(timeline=[])
        assert resp.timeline == []

    def test_serialization(self):
        resp = TimelineResponse(
            timeline=[TimelineEntry(month="2026-01", count=3)]
        )
        data = resp.model_dump()
        assert "timeline" in data
        assert len(data["timeline"]) == 1
        assert data["timeline"][0]["month"] == "2026-01"
