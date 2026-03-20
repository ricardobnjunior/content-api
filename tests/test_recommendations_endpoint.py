"""Tests for app/api/endpoints/recommendations.py — similar articles API endpoint."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

# Set required environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_endpoint.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-endpoint")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key-endpoint")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")


def _make_article_orm(
    article_id: int,
    title: str,
    content: str = "Some content",
    status: str = "published",
):
    """Create a MagicMock that behaves like an Article ORM object."""
    article = MagicMock()
    article.id = article_id
    article.title = title
    article.content = content
    article.status = status
    return article


def _make_llm_response(similar: list[dict]) -> MagicMock:
    """Create a mock LLM API response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({"similar": similar})
    return mock_response


@pytest.fixture
def client():
    """Create a TestClient with mocked database."""
    from starlette.testclient import TestClient

    from app.main import app  # noqa: E402

    with TestClient(app) as c:
        yield c


class TestGetSimilarArticlesHappyPath:
    """Happy path tests for GET /api/v1/recommendations/{article_id}/similar."""

    def test_returns_similar_articles_with_scores(self, client):
        """Returns similar articles when multiple published articles exist."""
        target = _make_article_orm(1, "Target Article")
        candidate_a = _make_article_orm(2, "Related Article A")
        candidate_b = _make_article_orm(3, "Related Article B")

        llm_response = _make_llm_response([
            {"id": 2, "similarity_score": 0.85},
            {"id": 3, "similarity_score": 0.60},
        ])

        with (
            patch("app.api.endpoints.recommendations.get_article", return_value=target),
            patch(
                "app.api.endpoints.recommendations.get_articles",
                return_value=[target, candidate_a, candidate_b],
            ),
            patch("app.ai.similarity.OpenAI") as mock_openai_cls,
        ):
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = llm_response

            response = client.get("/api/v1/recommendations/1/similar")

        assert response.status_code == 200
        data = response.json()
        assert data["article_id"] == 1
        assert len(data["similar_articles"]) == 2
        assert data["similar_articles"][0]["id"] == 2
        assert data["similar_articles"][0]["title"] == "Related Article A"
        assert data["similar_articles"][0]["similarity_score"] == pytest.approx(0.85)
        assert data["similar_articles"][1]["id"] == 3
        assert data["similar_articles"][1]["title"] == "Related Article B"

    def test_response_structure_matches_schema(self, client):
        """Response contains required fields: article_id, similar_articles."""
        target = _make_article_orm(5, "Some Article")
        candidate = _make_article_orm(6, "Another Article")

        llm_response = _make_llm_response([{"id": 6, "similarity_score": 0.75}])

        with (
            patch("app.api.endpoints.recommendations.get_article", return_value=target),
            patch(
                "app.api.endpoints.recommendations.get_articles",
                return_value=[target, candidate],
            ),
            patch("app.ai.similarity.OpenAI") as mock_openai_cls,
        ):
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = llm_response

            response = client.get("/api/v1/recommendations/5/similar")

        assert response.status_code == 200
        data = response.json()
        assert "article_id" in data
        assert "similar_articles" in data
        assert isinstance(data["similar_articles"], list)

        item = data["similar_articles"][0]
        assert "id" in item
        assert "title" in item
        assert "similarity_score" in item

    def test_default_limit_is_five(self, client):
        """Default limit of 5 is used when not specified."""
        target = _make_article_orm(1, "Target")
        # Create 7 candidates
        candidates = [_make_article_orm(i, f"Article {i}") for i in range(2, 9)]
        all_articles = [target] + candidates

        llm_similar = [{"id": i, "similarity_score": 1.0 - i * 0.1} for i in range(2, 9)]
        llm_response = _make_llm_response(llm_similar)

        with (
            patch("app.api.endpoints.recommendations.get_article", return_value=target),
            patch("app.api.endpoints.recommendations.get_articles", return_value=all_articles),
            patch("app.ai.similarity.OpenAI") as mock_openai_cls,
        ):
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = llm_response

            response = client.get("/api/v1/recommendations/1/similar")

        assert response.status_code == 200
        data = response.json()
        assert len(data["similar_articles"]) <= 5

    def test_custom_limit_parameter(self, client):
        """Custom limit parameter is respected."""
        target = _make_article_orm(1, "Target")
        candidates = [_make_article_orm(i, f"Article {i}") for i in range(2, 8)]
        all_articles = [target] + candidates

        llm_similar = [{"id": i, "similarity_score": 1.0 - (i - 2) * 0.1} for i in range(2, 8)]
        llm_response = _make_llm_response(llm_similar)

        with (
            patch("app.api.endpoints.recommendations.get_article", return_value=target),
            patch("app.api.endpoints.recommendations.get_articles", return_value=all_articles),
            patch("app.ai.similarity.OpenAI") as mock_openai_cls,
        ):
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = llm_response

            response = client.get("/api/v1/recommendations/1/similar?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data["similar_articles"]) <= 3


class TestGetSimilarArticlesEdgeCases:
    """Edge case tests for the recommendations endpoint."""

    def test_article_not_found_returns_404(self, client):
        """Returns 404 when the target article does not exist."""
        with patch("app.api.endpoints.recommendations.get_article", return_value=None):
            response = client.get("/api/v1/recommendations/9999/similar")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_only_one_published_article_returns_empty_list(self, client):
        """Returns empty similar_articles when no candidates exist."""
        target = _make_article_orm(1, "Only Article")

        with (
            patch("app.api.endpoints.recommendations.get_article", return_value=target),
            patch(
                "app.api.endpoints.recommendations.get_articles",
                return_value=[target],  # Only the target, no candidates
            ),
            patch("app.ai.similarity.OpenAI") as mock_openai_cls,
        ):
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client

            response = client.get("/api/v1/recommendations/1/similar")

            # LLM should NOT be called
            mock_client.chat.completions.create.assert_not_called()

        assert response.status_code == 200
        data = response.json()
        assert data["article_id"] == 1
        assert data["similar_articles"] == []

    def test_draft_articles_excluded_from_candidates(self, client):
        """Draft articles are not passed to the LLM as candidates."""
        target = _make_article_orm(1, "Published Target", status="published")
        draft = _make_article_orm(2, "Draft Article", status="draft")
        published = _make_article_orm(3, "Published Candidate", status="published")

        llm_response = _make_llm_response([{"id": 3, "similarity_score": 0.70}])

        captured_candidates = []

        def fake_find_similar(target_article, candidate_articles, limit):
            captured_candidates.extend(candidate_articles)
            return [{"id": 3, "similarity_score": 0.70}]

        with (
            patch("app.api.endpoints.recommendations.get_article", return_value=target),
            patch(
                "app.api.endpoints.recommendations.get_articles",
                return_value=[target, draft, published],
            ),
            patch(
                "app.api.endpoints.recommendations.find_similar_articles",
                side_effect=fake_find_similar,
            ),
        ):
            response = client.get("/api/v1/recommendations/1/similar")

        assert response.status_code == 200
        candidate_ids = [c.id for c in captured_candidates]
        assert 2 not in candidate_ids  # Draft should be excluded
        assert 3 in candidate_ids  # Published should be included

    def test_target_article_excluded_from_candidates(self, client):
        """The target article itself is not included in candidates."""
        target = _make_article_orm(1, "Target Article", status="published")
        other = _make_article_orm(2, "Other Article", status="published")

        captured_candidates = []

        def fake_find_similar(target_article, candidate_articles, limit):
            captured_candidates.extend(candidate_articles)
            return [{"id": 2, "similarity_score": 0.80}]

        with (
            patch("app.api.endpoints.recommendations.get_article", return_value=target),
            patch(
                "app.api.endpoints.recommendations.get_articles",
                return_value=[target, other],
            ),
            patch(
                "app.api.endpoints.recommendations.find_similar_articles",
                side_effect=fake_find_similar,
            ),
        ):
            response = client.get("/api/v1/recommendations/1/similar")

        assert response.status_code == 200
        candidate_ids = [c.id for c in captured_candidates]
        assert 1 not in candidate_ids  # Target should not be in candidates

    def test_llm_api_failure_returns_500(self, client):
        """Returns 500 when the LLM API call fails."""
        target = _make_article_orm(1, "Target Article")
        candidate = _make_article_orm(2, "Candidate Article")

        with (
            patch("app.api.endpoints.recommendations.get_article", return_value=target),
            patch(
                "app.api.endpoints.recommendations.get_articles",
                return_value=[target, candidate],
            ),
            patch(
                "app.api.endpoints.recommendations.find_similar_articles",
                side_effect=RuntimeError("LLM API call failed: connection timeout"),
            ),
        ):
            response = client.get("/api/v1/recommendations/1/similar")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    def test_malformed_llm_json_returns_500(self, client):
        """Returns 500 when the LLM returns malformed JSON (via ValueError)."""
        target = _make_article_orm(1, "Target Article")
        candidate = _make_article_orm(2, "Candidate Article")

        with (
            patch("app.api.endpoints.recommendations.get_article", return_value=target),
            patch(
                "app.api.endpoints.recommendations.get_articles",
                return_value=[target, candidate],
            ),
            patch(
                "app.api.endpoints.recommendations.find_similar_articles",
                side_effect=ValueError("LLM returned malformed JSON"),
            ),
        ):
            response = client.get("/api/v1/recommendations/1/similar")

        assert response.status_code == 500

    def test_all_articles_are_drafts_returns_empty_list(self, client):
        """Returns empty list when all other articles are drafts."""
        target = _make_article_orm(1, "Target", status="published")
        draft1 = _make_article_orm(2, "Draft 1", status="draft")
        draft2 = _make_article_orm(3, "Draft 2", status="draft")

        with (
            patch("app.api.endpoints.recommendations.get_article", return_value=target),
            patch(
                "app.api.endpoints.recommendations.get_articles",
                return_value=[target, draft1, draft2],
            ),
            patch("app.ai.similarity.OpenAI") as mock_openai_cls,
        ):
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client

            response = client.get("/api/v1/recommendations/1/similar")

            mock_client.chat.completions.create.assert_not_called()

        assert response.status_code == 200
        assert response.json()["similar_articles"] == []

    def test_limit_query_param_validation_too_low(self, client):
        """Returns 422 when limit is less than 1."""
        target = _make_article_orm(1, "Target Article")

        with patch("app.api.endpoints.recommendations.get_article", return_value=target):
            response = client.get("/api/v1/recommendations/1/similar?limit=0")

        assert response.status_code == 422

    def test_limit_query_param_validation_too_high(self, client):
        """Returns 422 when limit exceeds 50."""
        target = _make_article_orm(1, "Target Article")

        with patch("app.api.endpoints.recommendations.get_article", return_value=target):
            response = client.get("/api/v1/recommendations/1/similar?limit=51")

        assert response.status_code == 422


class TestRecommendationsRouterIntegration:
    """Integration tests verifying the router is mounted correctly."""

    def test_endpoint_is_accessible_at_correct_path(self, client):
        """The recommendations endpoint is reachable at /api/v1/recommendations/."""
        with patch("app.api.endpoints.recommendations.get_article", return_value=None):
            response = client.get("/api/v1/recommendations/1/similar")

        # 404 (article not found) means the route exists and handled the request
        assert response.status_code == 404

    def test_non_integer_article_id_returns_422(self, client):
        """Returns 422 when article_id is not an integer."""
        response = client.get("/api/v1/recommendations/not-an-id/similar")
        assert response.status_code == 422
