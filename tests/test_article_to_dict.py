"""Unit tests for the _article_to_dict helper function."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


COLUMN_NAMES = ["id", "title", "content", "status", "image_url", "created_at", "updated_at"]


def _make_column_mock(name):
    col = MagicMock()
    col.name = name
    return col


def _make_article_mock(**kwargs):
    article = MagicMock()
    defaults = {
        "id": 1,
        "title": "Title",
        "content": "Content",
        "status": "published",
        "image_url": None,
        "created_at": datetime(2024, 1, 1, 0, 0, 0),
        "updated_at": datetime(2024, 1, 2, 0, 0, 0),
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(article, k, v)
    return article


@pytest.fixture(autouse=True)
def patch_table_columns():
    """Patch Article.__table__.columns for all tests in this module."""
    columns = [_make_column_mock(n) for n in COLUMN_NAMES]
    with patch("app.api.endpoints.export.Article.__table__.columns", columns):
        yield


# Import after patching is set up via autouse fixture
# We need to import inside tests because the module-level patch must be active.

class TestArticleToDict:
    def test_returns_dict(self):
        from app.api.endpoints.export import _article_to_dict
        article = _make_article_mock()
        result = _article_to_dict(article)
        assert isinstance(result, dict)

    def test_all_columns_present(self):
        from app.api.endpoints.export import _article_to_dict
        article = _make_article_mock()
        result = _article_to_dict(article)
        for name in COLUMN_NAMES:
            assert name in result

    def test_datetime_converted_to_iso(self):
        from app.api.endpoints.export import _article_to_dict
        dt = datetime(2024, 6, 15, 10, 30, 0)
        article = _make_article_mock(created_at=dt, updated_at=dt)
        result = _article_to_dict(article)
        assert result["created_at"] == "2024-06-15T10:30:00"
        assert result["updated_at"] == "2024-06-15T10:30:00"

    def test_non_datetime_fields_unchanged(self):
        from app.api.endpoints.export import _article_to_dict
        article = _make_article_mock(id=99, title="My Title", status="draft")
        result = _article_to_dict(article)
        assert result["id"] == 99
        assert result["title"] == "My Title"
        assert result["status"] == "draft"

    def test_null_image_url_preserved(self):
        from app.api.endpoints.export import _article_to_dict
        article = _make_article_mock(image_url=None)
        result = _article_to_dict(article)
        assert result["image_url"] is None

    def test_image_url_with_value(self):
        from app.api.endpoints.export import _article_to_dict
        article = _make_article_mock(image_url="http://example.com/img.png")
        result = _article_to_dict(article)
        assert result["image_url"] == "http://example.com/img.png"

    def test_string_status_not_converted(self):
        from app.api.endpoints.export import _article_to_dict
        article = _make_article_mock(status="published")
        result = _article_to_dict(article)
        assert isinstance(result["status"], str)
        assert result["status"] == "published"


class TestBuildCSVResponse:
    def test_returns_streaming_response(self):
        from fastapi.responses import StreamingResponse
        from app.api.endpoints.export import _build_csv_response
        result = _build_csv_response([])
        assert isinstance(result, StreamingResponse)

    def test_media_type_is_csv(self):
        from app.api.endpoints.export import _build_csv_response
        result = _build_csv_response([])
        assert result.media_type == "text/csv"

    def test_content_disposition_header(self):
        from app.api.endpoints.export import _build_csv_response
        result = _build_csv_response([])
        assert 'filename="articles.csv"' in result.headers["content-disposition"]

    def test_empty_input_produces_header_only(self):
        from app.api.endpoints.export import _build_csv_response
        import io as _io
        import csv as _csv

        response = _build_csv_response([])
        # Collect stream
        body = b"".join(response.body_iterator)
        text = body.decode("utf-8")
        lines = text.strip().splitlines()
        assert len(lines) == 1
        assert "id" in lines[0]

    def test_one_article_produces_header_plus_one_row(self):
        from app.api.endpoints.export import _build_csv_response
        article_dict = {
            "id": 1,
            "title": "T",
            "content": "C",
            "status": "published",
            "image_url": None,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
        }
        response = _build_csv_response([article_dict])
        body = b"".join(response.body_iterator)
        lines = body.decode("utf-8").strip().splitlines()
        assert len(lines) == 2


class TestBuildJSONResponse:
    def test_returns_streaming_response(self):
        from fastapi.responses import StreamingResponse
        from app.api.endpoints.export import _build_json_response
        result = _build_json_response([])
        assert isinstance(result, StreamingResponse)

    def test_media_type_is_json(self):
        from app.api.endpoints.export import _build_json_response
        result = _build_json_response([])
        assert result.media_type == "application/json"

    def test_content_disposition_header(self):
        from app.api.endpoints.export import _build_json_response
        result = _build_json_response([])
        assert 'filename="articles.json"' in result.headers["content-disposition"]

    def test_empty_list_returns_empty_json_array(self):
        import json as _json
        from app.api.endpoints.export import _build_json_response
        response = _build_json_response([])
        body = b"".join(response.body_iterator)
        data = _json.loads(body.decode("utf-8"))
        assert data == []

    def test_articles_serialized_correctly(self):
        import json as _json
        from app.api.endpoints.export import _build_json_response
        articles = [
            {"id": 1, "title": "A", "content": "B", "status": "draft",
             "image_url": None, "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-02T00:00:00"},
            {"id": 2, "title": "C", "content": "D", "status": "published",
             "image_url": "http://x.com/img.png", "created_at": "2024-02-01T00:00:00", "updated_at": "2024-02-02T00:00:00"},
        ]
        response = _build_json_response(articles)
        body = b"".join(response.body_iterator)
        data = _json.loads(body.decode("utf-8"))
        assert len(data) == 2
        assert data[0]["title"] == "A"
        assert data[1]["title"] == "C"
        assert data[1]["image_url"] == "http://x.com/img.png"
