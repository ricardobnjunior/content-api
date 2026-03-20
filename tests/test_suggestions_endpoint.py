"""Tests for the /api/v1/suggestions/categories/{article_id} endpoint."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

# Patch settings before importing the app to avoid real DB / env requirements
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_suggestions.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")


def make_mock_llm_response(content: str) -> MagicMock:
    """Build a mock OpenAI response object."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = content
    return mock_response


@pytest.fixture
def client():
    """Create a TestClient with the FastAPI app."""
    from app.main import app  # noqa: E402
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Provide a mock SQLAlchemy session."""
    return MagicMock()


def _make_article(article_id: int = 1, title: str = "Test Article", content: str = "Test content"):
    """Create a mock article object."""
    article = MagicMock()
    article.id = article_id
    article.title = title
    article.content = content
    return article


def _make_category(cat_id: int, name: str):
    """Create a mock category object."""
    cat = MagicMock()
    cat.id = cat_id
    cat.name = name
    return cat


@pytest.fixture(autouse=True)
def patch_get_db(mock_db_session):
    """Override the get_db dependency for all tests."""
    with patch("app.api.endpoints.suggestions.get_db", return_value=iter([mock_db_session])):
        yield mock_db_session


class TestGetCategorySuggestionsHappyPath:
    """Happy path tests for category suggestions endpoint."""

    def test_returns_suggestions_with_categories(self, client, mock_db_session):
        """Returns suggestions when article and categories exist and LLM responds."""
        article = _make_article(1, "AI Advances", "Machine learning content")
        categories = [
            _make_category(2, "Technology"),
            _make_category(5, "Science"),
        ]

        llm_json = json.dumps({
            "suggestions": [
                {"category_name": "Technology", "confidence": 0.85},
                {"category_name": "Science", "confidence": 0.62},
            ]
        })

        with patch("app.api.endpoints.suggestions.get_article", return_value=article), \
             patch("app.api.endpoints.suggestions.classify_article") as mock_classify:

            mock_classify.return_value = [
                {"category_name": "Technology", "confidence": 0.85},
                {"category_name": "Science", "confidence": 0.62},
            ]
            mock_db_session.query.return_value.all.return_value = categories

            response = client.get("/api/v1/suggestions/categories/1")

        assert response.status_code == 200
        data = response.json()
        assert data["article_id"] == 1
        assert len(data["suggestions"]) == 2
        assert data["suggestions"][0]["category_name"] == "Technology"
        assert data["suggestions"][0]["category_id"] == 2
        assert data["suggestions"][0]["confidence"] == pytest.approx(0.85)
        assert data["suggestions"][1]["category_name"] == "Science"
        assert data["suggestions"][1]["category_id"] == 5

    def test_returns_empty_suggestions_when_no_categories(self, client, mock_db_session):
        """Returns empty suggestions list when no categories exist in DB."""
        article = _make_article(1, "Some Article", "Some content")

        with patch("app.api.endpoints.suggestions.get_article", return_value=article), \
             patch("app.api.endpoints.suggestions.classify_article") as mock_classify:

            mock_db_session.query.return_value.all.return_value = []

            response = client.get("/api/v1/suggestions/categories/1")

            # LLM should NOT be called when there are no categories
            mock_classify.assert_not_called()

        assert response.status_code == 200
        data = response.json()
        assert data["article_id"] == 1
        assert data["suggestions"] == []

    def test_limit_parameter_respected(self, client, mock_db_session):
        """Custom limit parameter is passed to classify_article."""
        article = _make_article(1, "Article", "Content")
        categories = [
            _make_category(1, "Technology"),
            _make_category(2, "Science"),
            _make_category(3, "Sports"),
        ]

        with patch("app.api.endpoints.suggestions.get_article", return_value=article), \
             patch("app.api.endpoints.suggestions.classify_article") as mock_classify:

            mock_classify.return_value = [
                {"category_name": "Technology", "confidence": 0.9},
            ]
            mock_db_session.query.return_value.all.return_value = categories

            response = client.get("/api/v1/suggestions/categories/1?limit=1")

        assert response.status_code == 200
        mock_classify.assert_called_once()
        call_kwargs = mock_classify.call_args
        assert call_kwargs.kwargs["limit"] == 1 or call_kwargs.args[3] == 1

    def test_default_limit_is_3(self, client, mock_db_session):
        """Default limit of 3 is used when not specified."""
        article = _make_article(1, "Article", "Content")
        categories = [_make_category(1, "Technology")]

        with patch("app.api.endpoints.suggestions.get_article", return_value=article), \
             patch("app.api.endpoints.suggestions.classify_article") as mock_classify:

            mock_classify.return_value = []
            mock_db_session.query.return_value.all.return_value = categories

            response = client.get("/api/v1/suggestions/categories/1")

        assert response.status_code == 200
        # Default limit=3 should have been passed
        call_kwargs = mock_classify.call_args
        limit_value = (
            call_kwargs.kwargs.get("limit")
            if call_kwargs.kwargs
            else call_kwargs.args[3]
        )
        assert limit_value == 3


class TestGetCategorySuggestionsErrorCases:
    """Error case tests for category suggestions endpoint."""

    def test_article_not_found_returns_404(self, client, mock_db_session):
        """Returns 404 when article does not exist."""
        with patch("app.api.endpoints.suggestions.get_article", return_value=None):
            response = client.get("/api/v1/suggestions/categories/9999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_llm_failure_returns_500(self, client, mock_db_session):
        """Returns 500 when LLM classifier raises an exception."""
        article = _make_article(1, "Article", "Content")
        categories = [_make_category(1, "Technology")]

        with patch("app.api.endpoints.suggestions.get_article", return_value=article), \
             patch("app.api.endpoints.suggestions.classify_article",
                   side_effect=Exception("OpenRouter API timeout")):

            mock_db_session.query.return_value.all.return_value = categories

            response = client.get("/api/v1/suggestions/categories/1")

        assert response.status_code == 500
        assert "LLM classification failed" in response.json()["detail"]

    def test_llm_malformed_json_returns_500(self, client, mock_db_session):
        """Returns 500 when LLM returns malformed JSON (ValueError)."""
        article = _make_article(1, "Article", "Content")
        categories = [_make_category(1, "Technology")]

        with patch("app.api.endpoints.suggestions.get_article", return_value=article), \
             patch("app.api.endpoints.suggestions.classify_article",
                   side_effect=ValueError("LLM response missing 'suggestions' key")):

            mock_db_session.query.return_value.all.return_value = categories

            response = client.get("/api/v1/suggestions/categories/1")

        assert response.status_code == 500

    def test_invalid_limit_below_minimum_rejected(self, client, mock_db_session):
        """Limit=0 is rejected (ge=1 constraint)."""
        with patch("app.api.endpoints.suggestions.get_article", return_value=MagicMock()):
            response = client.get("/api/v1/suggestions/categories/1?limit=0")

        assert response.status_code == 422

    def test_response_structure_matches_schema(self, client, mock_db_session):
        """Response contains required fields matching the schema."""
        article = _make_article(42, "Schema Test", "Content")
        categories = [_make_category(10, "Technology")]

        with patch("app.api.endpoints.suggestions.get_article", return_value=article), \
             patch("app.api.endpoints.suggestions.classify_article") as mock_classify:

            mock_classify.return_value = [
                {"category_name": "Technology", "confidence": 0.75},
            ]
            mock_db_session.query.return_value.all.return_value = categories

            response = client.get("/api/v1/suggestions/categories/42")

        assert response.status_code == 200
        data = response.json()
        assert "article_id" in data
        assert "suggestions" in data
        assert data["article_id"] == 42
        for item in data["suggestions"]:
            assert "category_id" in item
            assert "category_name" in item
            assert "confidence" in item

    def test_unknown_category_from_classifier_skipped(self, client, mock_db_session):
        """Categories returned by classifier not in DB name_to_id are skipped."""
        article = _make_article(1, "Article", "Content")
        categories = [_make_category(1, "Technology")]

        with patch("app.api.endpoints.suggestions.get_article", return_value=article), \
             patch("app.api.endpoints.suggestions.classify_article") as mock_classify:

            # Classifier returns a category not in the DB (edge case)
            mock_classify.return_value = [
                {"category_name": "GhostCategory", "confidence": 0.9},
                {"category_name": "Technology", "confidence": 0.7},
            ]
            mock_db_session.query.return_value.all.return_value = categories

            response = client.get("/api/v1/suggestions/categories/1")

        assert response.status_code == 200
        data = response.json()
        names = [s["category_name"] for s in data["suggestions"]]
        assert "GhostCategory" not in names
        assert "Technology" in names
