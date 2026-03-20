"""Unit tests for Pydantic schemas in app/schemas/article.py."""

import pytest
from pydantic import ValidationError

from app.schemas.article import ArticleList, ArticleResponse, PaginationMeta
from app.models.article import ArticleStatus
from datetime import datetime


def _make_article_response(**kwargs) -> dict:
    """Return a valid ArticleResponse-compatible dict with optional overrides."""
    now = datetime.utcnow()
    base = {
        "id": 1,
        "title": "Test Title",
        "body": "Test body",
        "status": ArticleStatus.draft,
        "author": "Author",
        "categories": [],
        "created_at": now,
        "updated_at": now,
    }
    base.update(kwargs)
    return base


def _make_pagination_meta(**kwargs) -> dict:
    """Return a valid PaginationMeta-compatible dict with optional overrides."""
    base = {"total": 10, "page": 1, "per_page": 20, "pages": 1}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# PaginationMeta
# ---------------------------------------------------------------------------


def test_pagination_meta_happy_path() -> None:
    """PaginationMeta accepts valid fields."""
    meta = PaginationMeta(total=100, page=2, per_page=20, pages=5)
    assert meta.total == 100
    assert meta.page == 2
    assert meta.per_page == 20
    assert meta.pages == 5


def test_pagination_meta_zero_total() -> None:
    """PaginationMeta with total=0 and pages=0 is valid."""
    meta = PaginationMeta(total=0, page=1, per_page=20, pages=0)
    assert meta.total == 0
    assert meta.pages == 0


def test_pagination_meta_missing_field() -> None:
    """PaginationMeta raises ValidationError when a required field is missing."""
    with pytest.raises(ValidationError):
        PaginationMeta(total=10, page=1, per_page=20)  # missing pages


# ---------------------------------------------------------------------------
# ArticleList
# ---------------------------------------------------------------------------


def test_article_list_happy_path() -> None:
    """ArticleList with valid items and meta is constructed correctly."""
    article_data = _make_article_response()
    meta_data = _make_pagination_meta()

    article_response = ArticleResponse(**article_data)
    meta = PaginationMeta(**meta_data)

    article_list = ArticleList(items=[article_response], meta=meta)
    assert len(article_list.items) == 1
    assert article_list.meta.total == 10


def test_article_list_empty_items() -> None:
    """ArticleList with empty items list is valid."""
    meta = PaginationMeta(total=0, page=1, per_page=20, pages=0)
    article_list = ArticleList(items=[], meta=meta)
    assert article_list.items == []
    assert article_list.meta.total == 0


def test_article_list_missing_meta() -> None:
    """ArticleList raises ValidationError when meta is missing."""
    article_data = _make_article_response()
    article_response = ArticleResponse(**article_data)

    with pytest.raises(ValidationError):
        ArticleList(items=[article_response])  # missing meta


# ---------------------------------------------------------------------------
# ArticleResponse
# ---------------------------------------------------------------------------


def test_article_response_happy_path() -> None:
    """ArticleResponse validates correctly with all fields present."""
    data = _make_article_response()
    response = ArticleResponse(**data)

    assert response.id == 1
    assert response.title == "Test Title"
    assert response.status == ArticleStatus.draft
    assert response.categories == []


def test_article_response_with_categories() -> None:
    """ArticleResponse with categories list is valid."""
    data = _make_article_response(
        categories=[{"id": 1, "name": "Tech"}, {"id": 2, "name": "Science"}]
    )
    response = ArticleResponse(**data)
    assert len(response.categories) == 2
    assert response.categories[0].name == "Tech"


def test_article_response_missing_required_field() -> None:
    """ArticleResponse raises ValidationError when title is missing."""
    data = _make_article_response()
    data.pop("title")

    with pytest.raises(ValidationError):
        ArticleResponse(**data)
