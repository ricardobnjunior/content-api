"""Unit tests for the article_to_dict helper and generate_csv generator."""

import csv
import io
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


# ---------------------------------------------------------------------------
# Helper to build a fake Article column descriptor
# ---------------------------------------------------------------------------

def _make_column(name):
    col = MagicMock()
    col.name = name
    return col


def _build_article_mock(fields: dict):
    """
    Build a MagicMock Article whose __table__.columns iterates over `fields`.
    Each key in `fields` becomes a column name; the value is the attribute value.
    """
    article = MagicMock(spec_set=list(fields.keys()))
    columns = [_make_column(name) for name in fields]

    # Patch Article.__table__.columns at the module level
    for name, value in fields.items():
        setattr(article, name, value)

    return article, columns


# ---------------------------------------------------------------------------
# We test article_to_dict by patching Article.__table__.columns
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_article_table():
    """Patch Article.__table__ so tests don't need a real database."""
    columns = [
        _make_column("id"),
        _make_column("title"),
        _make_column("content"),
        _make_column("status"),
        _make_column("image_url"),
        _make_column("created_at"),
        _make_column("updated_at"),
    ]
    with patch("app.api.endpoints.export.Article") as mock_article_cls:
        mock_table = MagicMock()
        mock_table.columns = columns
        mock_article_cls.__table__ = mock_table
        yield mock_article_cls, columns


class TestArticleToDict:
    """Tests for the article_to_dict() helper."""

    def test_returns_dict(self, patch_article_table):
        """article_to_dict must return a dict."""
        from app.api.endpoints.export import article_to_dict

        _, columns = patch_article_table
        article = MagicMock()
        article.id = 1
        article.title = "T"
        article.content = "C"
        article.status = "published"
        article.image_url = None
        article.created_at = datetime(2024, 1, 1)
        article.updated_at = datetime(2024, 1, 2)

        result = article_to_dict(article)
        assert isinstance(result, dict)

    def test_all_columns_present(self, patch_article_table):
        """Every column name must be a key in the returned dict."""
        from app.api.endpoints.export import article_to_dict

        _, columns = patch_article_table
        article = MagicMock()
        article.id = 1
        article.title = "T"
        article.content = "C"
        article.status = "published"
        article.image_url = None
        article.created_at = datetime(2024, 1, 1)
        article.updated_at = datetime(2024, 1, 2)

        result = article_to_dict(article)
        for col in columns:
            assert col.name in result

    def test_datetime_converted_to_isoformat(self, patch_article_table):
        """Datetime values must be converted to ISO 8601 strings."""
        from app.api.endpoints.export import article_to_dict

        article = MagicMock()
        article.id = 1
        article.title = "T"
        article.content = "C"
        article.status = "published"
        article.image_url = None
        article.created_at = datetime(2024, 5, 20, 14, 30, 0)
        article.updated_at = datetime(2024, 5, 21, 8, 0, 0)

        result = article_to_dict(article)
        assert result["created_at"] == "2024-05-20T14:30:00"
        assert result["updated_at"] == "2024-05-21T08:00:00"

    def test_none_image_url_preserved(self, patch_article_table):
        """None values must remain None (no isoformat conversion attempted)."""
        from app.api.endpoints.export import article_to_dict

        article = MagicMock()
        article.id = 2
        article.title = "T"
        article.content = "C"
        article.status = "draft"
        article.image_url = None
        article.created_at = datetime(2024, 1, 1)
        article.updated_at = datetime(2024, 1, 1)

        result = article_to_dict(article)
        assert result["image_url"] is None

    def test_string_values_unchanged(self, patch_article_table):
        """Non-datetime, non-None values must pass through unchanged."""
        from app.api.endpoints.export import article_to_dict

        article = MagicMock()
        article.id = 10
        article.title = "My Title"
        article.content = "Body"
        article.status = "published"
        article.image_url = "http://img.com/a.png"
        article.created_at = datetime(2024, 1, 1)
        article.updated_at = datetime(2024, 1, 1)

        result = article_to_dict(article)
        assert result["id"] == 10
        assert result["title"] == "My Title"
        assert result["image_url"] == "http://img.com/a.png"


class TestGenerateCsv:
    """Tests for the generate_csv() streaming generator."""

    def test_yields_header_when_empty(self, patch_article_table):
        """generate_csv with no articles must yield at least a header chunk."""
        from app.api.endpoints.export import generate_csv

        chunks = list(generate_csv([]))
        assert len(chunks) >= 1
        header_text = "".join(chunks)
        assert "id" in header_text
        assert "title" in header_text

    def test_yields_one_chunk_per_article_plus_header(self, patch_article_table):
        """generate_csv must yield header + one chunk per article."""
        from app.api.endpoints.export import generate_csv

        articles = []
        for i in range(3):
            a = MagicMock()
            a.id = i
            a.title = f"Article {i}"
            a.content = "C"
            a.status = "published"
            a.image_url = None
            a.created_at = datetime(2024, 1, 1)
            a.updated_at = datetime(2024, 1, 1)
            articles.append(a)

        chunks = list(generate_csv(articles))
        # 1 header + 3 data chunks
        assert len(chunks) == 4

    def test_output_is_valid_csv(self, patch_article_table):
        """Concatenated chunks must be parseable as valid CSV."""
        from app.api.endpoints.export import generate_csv

        article = MagicMock()
        article.id = 1
        article.title = "CSV Article"
        article.content = "Content, with comma"
        article.status = "published"
        article.image_url = None
        article.created_at = datetime(2024, 2, 15, 10, 0, 0)
        article.updated_at = datetime(2024, 2, 16, 10, 0, 0)

        full_csv = "".join(generate_csv([article]))
        reader = csv.reader(io.StringIO(full_csv))
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0][0] == "id"  # header first column

    def test_header_columns_match_article_table(self, patch_article_table):
        """Header row must list exactly the Article table column names."""
        from app.api.endpoints.export import generate_csv

        _, columns = patch_article_table
        full_csv = "".join(generate_csv([]))
        reader = csv.reader(io.StringIO(full_csv))
        rows = [r for r in reader if r]
        header = rows[0]
        expected = [col.name for col in columns]
        assert header == expected
