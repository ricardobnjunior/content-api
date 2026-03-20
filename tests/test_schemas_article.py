"""Unit tests for Pydantic schemas in app/schemas/article.py."""

import pytest
from pydantic import ValidationError

from app.models.article import ArticleStatus
from app.schemas.article import ArticleCreate, ArticleList, ArticleResponse, ArticleUpdate


# ---------------------------------------------------------------------------
# ArticleCreate
# ---------------------------------------------------------------------------


def test_article_create_valid():
    """ArticleCreate accepts valid data."""
    schema = ArticleCreate(
        title="Hello World",
        body="Some body text",
        author="Alice",
    )
    assert schema.title == "Hello World"
    assert schema.status == ArticleStatus.draft


def test_article_create_default_status_is_draft():
    """ArticleCreate default status is draft."""
    schema = ArticleCreate(title="A", body="B", author="C")
    assert schema.status == ArticleStatus.draft


def test_article_create_explicit_published_status():
    """ArticleCreate accepts published status."""
    schema = ArticleCreate(
        title="Published", body="Body", author="Bob", status=ArticleStatus.published
    )
    assert schema.status == ArticleStatus.published


def test_article_create_empty_title_fails():
    """ArticleCreate rejects empty title."""
    with pytest.raises(ValidationError):
        ArticleCreate(title="", body="Body", author="Author")


def test_article_create_title_too_long_fails():
    """ArticleCreate rejects title longer than 200 characters."""
    with pytest.raises(ValidationError):
        ArticleCreate(title="x" * 201, body="Body", author="Author")


def test_article_create_title_exactly_200_passes():
    """ArticleCreate accepts title of exactly 200 characters."""
    schema = ArticleCreate(title="x" * 200, body="Body", author="Author")
    assert len(schema.title) == 200


def test_article_create_author_too_long_fails():
    """ArticleCreate rejects author longer than 100 characters."""
    with pytest.raises(ValidationError):
        ArticleCreate(title="Title", body="Body", author="a" * 101)


def test_article_create_author_exactly_100_passes():
    """ArticleCreate accepts author of exactly 100 characters."""
    schema = ArticleCreate(title="Title", body="Body", author="a" * 100)
    assert len(schema.author) == 100


def test_article_create_missing_body_fails():
    """ArticleCreate rejects missing body."""
    with pytest.raises(ValidationError):
        ArticleCreate(title="Title", author="Author")


def test_article_create_invalid_status_fails():
    """ArticleCreate rejects an invalid status string."""
    with pytest.raises(ValidationError):
        ArticleCreate(title="Title", body="Body", author="Author", status="deleted")


# ---------------------------------------------------------------------------
# ArticleUpdate
# ---------------------------------------------------------------------------


def test_article_update_all_optional():
    """ArticleUpdate can be instantiated with no fields."""
    schema = ArticleUpdate()
    assert schema.title is None
    assert schema.body is None
    assert schema.author is None
    assert schema.status is None


def test_article_update_single_field():
    """ArticleUpdate with only title is valid."""
    schema = ArticleUpdate(title="New Title")
    assert schema.title == "New Title"
    assert schema.body is None


def test_article_update_empty_title_fails():
    """ArticleUpdate rejects empty string for title."""
    with pytest.raises(ValidationError):
        ArticleUpdate(title="")


def test_article_update_title_too_long_fails():
    """ArticleUpdate rejects title longer than 200 characters."""
    with pytest.raises(ValidationError):
        ArticleUpdate(title="x" * 201)


def test_article_update_valid_status():
    """ArticleUpdate accepts valid status values."""
    schema = ArticleUpdate(status=ArticleStatus.published)
    assert schema.status == ArticleStatus.published


def test_article_update_invalid_status_fails():
    """ArticleUpdate rejects invalid status strings."""
    with pytest.raises(ValidationError):
        ArticleUpdate(status="archived")


# ---------------------------------------------------------------------------
# ArticleResponse
# ---------------------------------------------------------------------------


def test_article_response_from_dict():
    """ArticleResponse can be constructed from a plain dict."""
    data = {
        "id": 1,
        "title": "My Article",
        "body": "Body text",
        "author": "Author Name",
        "status": "draft",
        "created_at": None,
        "updated_at": None,
    }
    schema = ArticleResponse(**data)
    assert schema.id == 1
    assert schema.status == ArticleStatus.draft


def test_article_response_optional_timestamps():
    """ArticleResponse created_at and updated_at are optional."""
    schema = ArticleResponse(
        id=1,
        title="T",
        body="B",
        author="A",
        status=ArticleStatus.draft,
    )
    assert schema.created_at is None
    assert schema.updated_at is None


def test_article_response_from_attributes_config():
    """ArticleResponse has from_attributes=True in model config."""
    assert ArticleResponse.model_config.get("from_attributes") is True


# ---------------------------------------------------------------------------
# ArticleList
# ---------------------------------------------------------------------------


def test_article_list_empty():
    """ArticleList with empty items and total=0 is valid."""
    schema = ArticleList(items=[], total=0)
    assert schema.items == []
    assert schema.total == 0


def test_article_list_with_items():
    """ArticleList with items populates correctly."""
    item = ArticleResponse(
        id=1,
        title="Title",
        body="Body",
        author="Author",
        status=ArticleStatus.draft,
    )
    schema = ArticleList(items=[item], total=1)
    assert len(schema.items) == 1
    assert schema.total == 1


def test_article_list_total_independent_of_items():
    """ArticleList total does not have to match len(items) (pagination)."""
    item = ArticleResponse(
        id=1,
        title="Title",
        body="Body",
        author="Author",
        status=ArticleStatus.draft,
    )
    schema = ArticleList(items=[item], total=100)
    assert schema.total == 100
    assert len(schema.items) == 1
