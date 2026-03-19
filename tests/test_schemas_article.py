"""Unit tests for Article Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.models.article import ArticleStatus
from app.schemas.article import ArticleCreate, ArticleList, ArticleResponse, ArticleUpdate


# ---------------------------------------------------------------------------
# ArticleCreate
# ---------------------------------------------------------------------------

class TestArticleCreate:
    def test_valid_minimal(self):
        """ArticleCreate with required fields and defaults is valid."""
        data = ArticleCreate(title="Hello", body="World", author="Alice")
        assert data.title == "Hello"
        assert data.body == "World"
        assert data.author == "Alice"
        assert data.status == ArticleStatus.draft

    def test_explicit_published_status(self):
        """ArticleCreate accepts published status."""
        data = ArticleCreate(
            title="Hello", body="World", author="Alice", status=ArticleStatus.published
        )
        assert data.status == ArticleStatus.published

    def test_title_empty_raises(self):
        """ArticleCreate rejects empty title (min_length=1)."""
        with pytest.raises(ValidationError):
            ArticleCreate(title="", body="Body", author="Author")

    def test_title_too_long_raises(self):
        """ArticleCreate rejects title longer than 200 chars."""
        with pytest.raises(ValidationError):
            ArticleCreate(title="A" * 201, body="Body", author="Author")

    def test_title_at_max_length_valid(self):
        """ArticleCreate accepts title exactly 200 chars."""
        data = ArticleCreate(title="A" * 200, body="Body", author="Author")
        assert len(data.title) == 200

    def test_author_empty_raises(self):
        """ArticleCreate rejects empty author (min_length=1)."""
        with pytest.raises(ValidationError):
            ArticleCreate(title="Title", body="Body", author="")

    def test_author_too_long_raises(self):
        """ArticleCreate rejects author longer than 100 chars."""
        with pytest.raises(ValidationError):
            ArticleCreate(title="Title", body="Body", author="A" * 101)

    def test_body_empty_raises(self):
        """ArticleCreate rejects empty body (min_length=1)."""
        with pytest.raises(ValidationError):
            ArticleCreate(title="Title", body="", author="Author")

    def test_invalid_status_raises(self):
        """ArticleCreate rejects an unknown status value."""
        with pytest.raises(ValidationError):
            ArticleCreate(title="Title", body="Body", author="Author", status="unknown")

    def test_missing_title_raises(self):
        """ArticleCreate without title raises ValidationError."""
        with pytest.raises(ValidationError):
            ArticleCreate(body="Body", author="Author")

    def test_missing_body_raises(self):
        """ArticleCreate without body raises ValidationError."""
        with pytest.raises(ValidationError):
            ArticleCreate(title="Title", author="Author")

    def test_missing_author_raises(self):
        """ArticleCreate without author raises ValidationError."""
        with pytest.raises(ValidationError):
            ArticleCreate(title="Title", body="Body")


# ---------------------------------------------------------------------------
# ArticleUpdate
# ---------------------------------------------------------------------------

class TestArticleUpdate:
    def test_all_optional_empty_is_valid(self):
        """ArticleUpdate with no fields is valid (all optional)."""
        data = ArticleUpdate()
        assert data.title is None
        assert data.body is None
        assert data.author is None
        assert data.status is None

    def test_partial_update_title_only(self):
        """ArticleUpdate with only title is valid."""
        data = ArticleUpdate(title="New Title")
        assert data.title == "New Title"
        assert data.body is None

    def test_title_empty_raises(self):
        """ArticleUpdate rejects empty title string."""
        with pytest.raises(ValidationError):
            ArticleUpdate(title="")

    def test_title_too_long_raises(self):
        """ArticleUpdate rejects title longer than 200 chars."""
        with pytest.raises(ValidationError):
            ArticleUpdate(title="A" * 201)

    def test_author_too_long_raises(self):
        """ArticleUpdate rejects author longer than 100 chars."""
        with pytest.raises(ValidationError):
            ArticleUpdate(author="A" * 101)

    def test_status_valid(self):
        """ArticleUpdate accepts a valid status."""
        data = ArticleUpdate(status=ArticleStatus.published)
        assert data.status == ArticleStatus.published

    def test_invalid_status_raises(self):
        """ArticleUpdate rejects an unknown status value."""
        with pytest.raises(ValidationError):
            ArticleUpdate(status="garbage")

    def test_model_dump_exclude_unset(self):
        """model_dump(exclude_unset=True) only includes explicitly set fields."""
        data = ArticleUpdate(title="Only Title")
        dumped = data.model_dump(exclude_unset=True)
        assert dumped == {"title": "Only Title"}

    def test_model_dump_include_all_when_set(self):
        """model_dump(exclude_unset=True) includes all fields when all are set."""
        data = ArticleUpdate(
            title="T", body="B", author="A", status=ArticleStatus.draft
        )
        dumped = data.model_dump(exclude_unset=True)
        assert set(dumped.keys()) == {"title", "body", "author", "status"}


# ---------------------------------------------------------------------------
# ArticleResponse
# ---------------------------------------------------------------------------

class TestArticleResponse:
    def test_from_dict_valid(self):
        """ArticleResponse can be constructed from a plain dict."""
        data = ArticleResponse(
            id=1,
            title="Title",
            body="Body",
            author="Author",
            status=ArticleStatus.draft,
            created_at=None,
            updated_at=None,
        )
        assert data.id == 1
        assert data.status == ArticleStatus.draft
        assert data.created_at is None
        assert data.updated_at is None

    def test_from_attributes_config(self):
        """ArticleResponse has from_attributes=True in its config."""
        assert ArticleResponse.model_config.get("from_attributes") is True

    def test_missing_required_field_raises(self):
        """ArticleResponse without required id raises ValidationError."""
        with pytest.raises(ValidationError):
            ArticleResponse(title="T", body="B", author="A", status=ArticleStatus.draft)


# ---------------------------------------------------------------------------
# ArticleList
# ---------------------------------------------------------------------------

class TestArticleList:
    def test_empty_list(self):
        """ArticleList with empty items list is valid."""
        data = ArticleList(items=[], total=0)
        assert data.items == []
        assert data.total == 0

    def test_with_items(self):
        """ArticleList correctly holds a list of ArticleResponse objects."""
        item = ArticleResponse(
            id=1,
            title="T",
            body="B",
            author="A",
            status=ArticleStatus.draft,
        )
        data = ArticleList(items=[item], total=1)
        assert len(data.items) == 1
        assert data.total == 1

    def test_missing_total_raises(self):
        """ArticleList without total raises ValidationError."""
        with pytest.raises(ValidationError):
            ArticleList(items=[])

    def test_missing_items_raises(self):
        """ArticleList without items raises ValidationError."""
        with pytest.raises(ValidationError):
            ArticleList(total=0)
