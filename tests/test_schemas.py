"""Tests for article Pydantic schemas — PaginationMeta and ArticleList."""

import math

import pytest

from app.models.article import ArticleStatus
from app.schemas.article import ArticleList, ArticleResponse, PaginationMeta


def test_pagination_meta_valid():
    """PaginationMeta accepts valid values."""
    meta = PaginationMeta(total=50, page=2, per_page=10, pages=5)
    assert meta.total == 50
    assert meta.page == 2
    assert meta.per_page == 10
    assert meta.pages == 5


def test_pagination_meta_zero_total():
    """PaginationMeta accepts zero total (empty results)."""
    meta = PaginationMeta(total=0, page=1, per_page=20, pages=0)
    assert meta.total == 0
    assert meta.pages == 0


def test_article_list_with_items():
    """ArticleList with items and meta serializes correctly."""
    article = ArticleResponse(
        id=1,
        title="Test",
        body="Body",
        status=ArticleStatus.draft,
        author="Alice",
        categories=[],
    )
    meta = PaginationMeta(total=1, page=1, per_page=20, pages=1)
    article_list = ArticleList(items=[article], meta=meta)
    assert len(article_list.items) == 1
    assert article_list.meta.total == 1


def test_article_list_empty():
    """ArticleList with empty items list is valid."""
    meta = PaginationMeta(total=0, page=1, per_page=20, pages=0)
    article_list = ArticleList(items=[], meta=meta)
    assert article_list.items == []
    assert article_list.meta.total == 0


def test_pagination_pages_calculation():
    """pages = ceil(total / per_page) is consistent."""
    for total, per_page in [(0, 10), (1, 10), (10, 10), (11, 10), (100, 7)]:
        expected_pages = math.ceil(total / per_page) if total > 0 else 0
        meta = PaginationMeta(
            total=total,
            page=1,
            per_page=per_page,
            pages=expected_pages,
        )
        assert meta.pages == expected_pages


def test_article_response_from_attributes():
    """ArticleResponse model_config from_attributes is set."""
    config = ArticleResponse.model_config
    assert config.get("from_attributes") is True


def test_pagination_meta_required_fields():
    """PaginationMeta requires all four fields."""
    with pytest.raises(Exception):
        PaginationMeta(total=10, page=1, per_page=20)  # missing pages


def test_article_list_categories_populated():
    """ArticleList items can include categories."""
    from app.schemas.article import CategoryResponse

    cat = CategoryResponse(id=1, name="Tech", slug="tech")
    article = ArticleResponse(
        id=2,
        title="Tech Article",
        body="Content",
        status=ArticleStatus.published,
        author="Bob",
        categories=[cat],
    )
    meta = PaginationMeta(total=1, page=1, per_page=20, pages=1)
    article_list = ArticleList(items=[article], meta=meta)
    assert article_list.items[0].categories[0].name == "Tech"
