"""Tests for the export articles endpoint (CSV and JSON)."""

import csv
import io
import json
import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def make_article(
    id=1,
    title="Test Article",
    content="Some content",
    status="published",
    image_url=None,
    created_at=None,
    updated_at=None,
):
    """Return a MagicMock that mimics an Article ORM instance."""
    article = MagicMock()
    article.id = id
    article.title = title
    article.content = content
    article.status = status
    article.image_url = image_url
    article.created_at = created_at or datetime(2024, 1, 15, 10, 0, 0)
    article.updated_at = updated_at or datetime(2024, 1, 16, 12, 0, 0)
    return article


@pytest.fixture()
def mock_db():
    """Return a mock SQLAlchemy Session."""
    return MagicMock()


@pytest.fixture()
def client(mock_db):
    """TestClient with the database dependency overridden."""
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


# ---------------------------------------------------------------------------
# CSV export — happy path
# ---------------------------------------------------------------------------

class TestCsvExport:
    """Tests for format=csv."""

    def test_csv_content_type(self, client, mock_db):
        """Response Content-Type must be text/csv."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_csv_content_disposition(self, client, mock_db):
        """Content-Disposition must trigger file download as articles.csv."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=csv")
        assert response.status_code == 200
        cd = response.headers.get("content-disposition", "")
        assert "attachment" in cd
        assert "articles.csv" in cd

    def test_csv_header_row_present(self, client, mock_db):
        """CSV must contain a header row with all expected column names."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=csv")
        assert response.status_code == 200

        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)
        assert len(rows) >= 1
        header = rows[0]
        for col in ("id", "title", "content", "status", "image_url", "created_at", "updated_at"):
            assert col in header, f"Column '{col}' missing from CSV header"

    def test_csv_empty_database_returns_only_header(self, client, mock_db):
        """With no articles the CSV must contain exactly one row (the header)."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=csv")
        assert response.status_code == 200

        reader = csv.reader(io.StringIO(response.text))
        rows = [r for r in reader if r]  # skip blank lines
        assert len(rows) == 1, f"Expected 1 header row, got {len(rows)}"

    def test_csv_with_articles_contains_data_rows(self, client, mock_db):
        """Each article must appear as a row after the header."""
        articles = [make_article(id=1, title="Alpha"), make_article(id=2, title="Beta")]
        mock_db.query.return_value.all.return_value = articles
        response = client.get("/api/v1/export/articles?format=csv")
        assert response.status_code == 200

        reader = csv.reader(io.StringIO(response.text))
        rows = [r for r in reader if r]
        assert len(rows) == 3, f"Expected header + 2 data rows, got {len(rows)}"

    def test_csv_data_row_contains_correct_values(self, client, mock_db):
        """Article field values must appear in the CSV data row."""
        article = make_article(
            id=42,
            title="Hello World",
            content="Body text",
            status="draft",
            image_url="http://example.com/img.png",
            created_at=datetime(2024, 3, 1, 9, 0, 0),
            updated_at=datetime(2024, 3, 2, 9, 0, 0),
        )
        mock_db.query.return_value.all.return_value = [article]
        response = client.get("/api/v1/export/articles?format=csv")
        assert response.status_code == 200

        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)
        header = rows[0]
        data = rows[1]
        row_dict = dict(zip(header, data))

        assert row_dict["id"] == "42"
        assert row_dict["title"] == "Hello World"
        assert row_dict["content"] == "Body text"
        assert row_dict["status"] == "draft"
        assert row_dict["image_url"] == "http://example.com/img.png"
        assert "2024-03-01" in row_dict["created_at"]
        assert "2024-03-02" in row_dict["updated_at"]

    def test_csv_null_image_url(self, client, mock_db):
        """NULL image_url should be present in the row (as empty string or None)."""
        article = make_article(id=5, image_url=None)
        mock_db.query.return_value.all.return_value = [article]
        response = client.get("/api/v1/export/articles?format=csv")
        assert response.status_code == 200

        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)
        # Just ensure we got two rows without error
        assert len([r for r in rows if r]) == 2


# ---------------------------------------------------------------------------
# JSON export — happy path
# ---------------------------------------------------------------------------

class TestJsonExport:
    """Tests for format=json."""

    def test_json_content_type(self, client, mock_db):
        """Response Content-Type must be application/json."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_json_content_disposition(self, client, mock_db):
        """Content-Disposition must trigger file download as articles.json."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=json")
        assert response.status_code == 200
        cd = response.headers.get("content-disposition", "")
        assert "attachment" in cd
        assert "articles.json" in cd

    def test_json_empty_database_returns_empty_array(self, client, mock_db):
        """With no articles the JSON body must be an empty array."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=json")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_json_with_articles_returns_array(self, client, mock_db):
        """JSON response must be an array with one object per article."""
        articles = [make_article(id=1), make_article(id=2)]
        mock_db.query.return_value.all.return_value = articles
        response = client.get("/api/v1/export/articles?format=json")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_json_article_contains_all_fields(self, client, mock_db):
        """Each JSON object must contain all article fields."""
        article = make_article(id=7, title="Field Check")
        mock_db.query.return_value.all.return_value = [article]
        response = client.get("/api/v1/export/articles?format=json")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        obj = data[0]
        for field in ("id", "title", "content", "status", "image_url", "created_at", "updated_at"):
            assert field in obj, f"Field '{field}' missing from JSON object"

    def test_json_article_values_are_correct(self, client, mock_db):
        """Article field values in JSON must match the source data."""
        article = make_article(
            id=99,
            title="JSON Article",
            content="JSON body",
            status="published",
            image_url=None,
            created_at=datetime(2024, 6, 1, 8, 0, 0),
            updated_at=datetime(2024, 6, 2, 8, 0, 0),
        )
        mock_db.query.return_value.all.return_value = [article]
        response = client.get("/api/v1/export/articles?format=json")
        assert response.status_code == 200
        obj = response.json()[0]
        assert obj["id"] == 99
        assert obj["title"] == "JSON Article"
        assert obj["content"] == "JSON body"
        assert obj["status"] == "published"
        assert obj["image_url"] is None
        assert "2024-06-01" in obj["created_at"]
        assert "2024-06-02" in obj["updated_at"]

    def test_json_datetime_fields_are_strings(self, client, mock_db):
        """Datetime fields in JSON must be serialized as ISO strings, not objects."""
        article = make_article(id=3, created_at=datetime(2024, 1, 1), updated_at=datetime(2024, 1, 2))
        mock_db.query.return_value.all.return_value = [article]
        response = client.get("/api/v1/export/articles?format=json")
        assert response.status_code == 200
        obj = response.json()[0]
        assert isinstance(obj["created_at"], str)
        assert isinstance(obj["updated_at"], str)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestExportErrors:
    """Tests for invalid inputs."""

    def test_invalid_format_returns_400(self, client, mock_db):
        """An unsupported format value must return HTTP 400."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=xml")
        assert response.status_code == 400

    def test_invalid_format_error_message(self, client, mock_db):
        """The 400 error detail must say 'csv' or 'json'."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=xlsx")
        assert response.status_code == 400
        body = response.json()
        assert "csv" in body["detail"].lower() or "json" in body["detail"].lower()

    def test_missing_format_returns_error(self, client, mock_db):
        """Omitting the format query param must not return 200."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles")
        # FastAPI returns 422 for missing required Query param
        assert response.status_code in (400, 422)

    def test_empty_string_format_returns_400(self, client, mock_db):
        """An empty string format must return a non-200 response."""
        mock_db.query.return_value.all.return_value = []
        response = client.get("/api/v1/export/articles?format=")
        assert response.status_code in (400, 422)
