"""Tests for the export articles endpoint."""

import json
import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers to build fake Article ORM instances
# ---------------------------------------------------------------------------

def _make_article(
    id=1,
    title="Test Article",
    content="Test content",
    status="published",
    image_url=None,
    created_at=None,
    updated_at=None,
):
    """Return a MagicMock that behaves like an Article ORM instance."""
    article = MagicMock()
    article.id = id
    article.title = title
    article.content = content
    article.status = status
    article.image_url = image_url
    article.created_at = created_at or datetime(2024, 1, 1, 12, 0, 0)
    article.updated_at = updated_at or datetime(2024, 1, 2, 12, 0, 0)
    return article


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_db():
    """Return a mock SQLAlchemy Session."""
    return MagicMock()


@pytest.fixture()
def client(mock_db):
    """Create a TestClient with the DB dependency overridden."""
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "sqlite:///./test_export.db", "SECRET_KEY": "testsecret"},
        clear=False,
    ):
        from app.main import app  # noqa: E402
        from app.database import get_db  # noqa: E402

        app.dependency_overrides[get_db] = lambda: mock_db
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()


@pytest.fixture()
def two_articles():
    """Return two fake article objects."""
    return [
        _make_article(id=1, title="Article One", content="Content one", status="published"),
        _make_article(id=2, title="Article Two", content="Content two", status="draft"),
    ]


# ---------------------------------------------------------------------------
# Helper: set up Article.__table__.columns mock
# ---------------------------------------------------------------------------

COLUMN_NAMES = ["id", "title", "content", "status", "image_url", "created_at", "updated_at"]


def _make_column_mock(name):
    col = MagicMock()
    col.name = name
    return col


def _patch_article_table():
    """Return a context manager that patches Article.__table__.columns."""
    columns = [_make_column_mock(n) for n in COLUMN_NAMES]
    return patch("app.api.endpoints.export.Article.__table__.columns", columns)


# ---------------------------------------------------------------------------
# CSV export — happy path
# ---------------------------------------------------------------------------

class TestCSVExport:
    def test_csv_content_type(self, client, mock_db, two_articles):
        mock_db.query.return_value.all.return_value = two_articles
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_csv_content_disposition(self, client, mock_db, two_articles):
        mock_db.query.return_value.all.return_value = two_articles
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=csv")
        assert response.status_code == 200
        assert 'filename="articles.csv"' in response.headers["content-disposition"]

    def test_csv_has_header_row(self, client, mock_db, two_articles):
        mock_db.query.return_value.all.return_value = two_articles
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=csv")
        lines = response.text.strip().splitlines()
        header = lines[0]
        assert "id" in header
        assert "title" in header
        assert "content" in header
        assert "status" in header
        assert "created_at" in header
        assert "updated_at" in header

    def test_csv_has_data_rows(self, client, mock_db, two_articles):
        mock_db.query.return_value.all.return_value = two_articles
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=csv")
        lines = response.text.strip().splitlines()
        # header + 2 data rows
        assert len(lines) == 3

    def test_csv_data_contains_article_values(self, client, mock_db, two_articles):
        mock_db.query.return_value.all.return_value = two_articles
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=csv")
        text = response.text
        assert "Article One" in text
        assert "Article Two" in text
        assert "published" in text
        assert "draft" in text

    def test_csv_all_fields_present(self, client, mock_db, two_articles):
        mock_db.query.return_value.all.return_value = two_articles
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=csv")
        lines = response.text.strip().splitlines()
        # Check data row has correct number of columns
        import csv as csv_mod
        reader = csv_mod.reader(lines)
        rows = list(reader)
        assert len(rows[0]) == len(COLUMN_NAMES)  # header columns
        assert len(rows[1]) == len(COLUMN_NAMES)  # first data row

    def test_csv_empty_database_returns_only_header(self, client, mock_db):
        mock_db.query.return_value.all.return_value = []
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=csv")
        assert response.status_code == 200
        lines = response.text.strip().splitlines()
        assert len(lines) == 1
        assert "id" in lines[0]

    def test_csv_datetime_as_iso_string(self, client, mock_db):
        article = _make_article(
            created_at=datetime(2024, 3, 15, 10, 30, 0),
            updated_at=datetime(2024, 3, 16, 11, 0, 0),
        )
        mock_db.query.return_value.all.return_value = [article]
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=csv")
        assert "2024-03-15" in response.text
        assert "2024-03-16" in response.text


# ---------------------------------------------------------------------------
# JSON export — happy path
# ---------------------------------------------------------------------------

class TestJSONExport:
    def test_json_content_type(self, client, mock_db, two_articles):
        mock_db.query.return_value.all.return_value = two_articles
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_json_content_disposition(self, client, mock_db, two_articles):
        mock_db.query.return_value.all.return_value = two_articles
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=json")
        assert 'filename="articles.json"' in response.headers["content-disposition"]

    def test_json_returns_valid_array(self, client, mock_db, two_articles):
        mock_db.query.return_value.all.return_value = two_articles
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=json")
        data = json.loads(response.text)
        assert isinstance(data, list)
        assert len(data) == 2

    def test_json_contains_all_fields(self, client, mock_db, two_articles):
        mock_db.query.return_value.all.return_value = two_articles
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=json")
        data = json.loads(response.text)
        first = data[0]
        for field in COLUMN_NAMES:
            assert field in first, f"Field '{field}' missing from JSON response"

    def test_json_values_match_article(self, client, mock_db):
        article = _make_article(
            id=42,
            title="Special Article",
            content="Special content",
            status="published",
        )
        mock_db.query.return_value.all.return_value = [article]
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=json")
        data = json.loads(response.text)
        assert data[0]["id"] == 42
        assert data[0]["title"] == "Special Article"
        assert data[0]["content"] == "Special content"
        assert data[0]["status"] == "published"

    def test_json_empty_database_returns_empty_array(self, client, mock_db):
        mock_db.query.return_value.all.return_value = []
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=json")
        assert response.status_code == 200
        data = json.loads(response.text)
        assert data == []

    def test_json_datetime_as_iso_string(self, client, mock_db):
        article = _make_article(
            created_at=datetime(2024, 5, 20, 8, 0, 0),
            updated_at=datetime(2024, 5, 21, 9, 0, 0),
        )
        mock_db.query.return_value.all.return_value = [article]
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=json")
        data = json.loads(response.text)
        assert data[0]["created_at"] == "2024-05-20T08:00:00"
        assert data[0]["updated_at"] == "2024-05-21T09:00:00"

    def test_json_null_image_url(self, client, mock_db):
        article = _make_article(image_url=None)
        mock_db.query.return_value.all.return_value = [article]
        with _patch_article_table():
            response = client.get("/api/v1/export/articles?format=json")
        data = json.loads(response.text)
        assert data[0]["image_url"] is None


# ---------------------------------------------------------------------------
# Invalid format — error path
# ---------------------------------------------------------------------------

class TestInvalidFormat:
    def test_invalid_format_returns_400(self, client, mock_db):
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=xml")
        assert response.status_code == 400

    def test_invalid_format_error_message(self, client, mock_db):
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=xml")
        body = response.json()
        assert "Format must be 'csv' or 'json'" in body["detail"]

    def test_missing_format_returns_422(self, client, mock_db):
        """format is required; missing it should return 422 Unprocessable Entity."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles")
        assert response.status_code == 422

    def test_empty_format_returns_400(self, client, mock_db):
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=")
        assert response.status_code == 400

    def test_uppercase_format_returns_400(self, client, mock_db):
        """Format check is case-sensitive; 'CSV' should not be accepted."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=CSV")
        assert response.status_code == 400

    def test_invalid_format_detail_type(self, client, mock_db):
        """Ensure the 400 response is proper JSON with a detail field."""
        response = client.get("/api/v1/export/articles?format=yaml")
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body
