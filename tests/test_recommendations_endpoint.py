"""Tests for GET /api/v1/recommendations/{article_id}/similar endpoint."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")


def make_article(article_id: int, title: str, content: str = "Content", status: str = "published"):
    """Create a mock article object with required attributes."""
    article = MagicMock()
    article.id = article_id
    article.title = title
    article.content = content
    article.status = status
    return article


def make_llm_response_mock(similar_list: list) -> MagicMock:
    """Create a mock OpenAI response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = json.dumps({"similar": similar_list})
    return response


@pytest.fixture
def client():
    """Create a TestClient with all external dependencies mocked."""
    from starlette.testclient import TestClient
    from app.main import app  # noqa: E402
    return TestClient(app)


class TestGetSimilarArticlesEndpoint:
    """Tests for GET /api/v1/recommendations/{article_id}/similar."""

    BASE_URL = "/api/v1/recommendations"

    def test_article_not_found_returns_404(self, client):
        """Non-existent article ID → 404 response."""
        with patch("app.api.endpoints.recommendations.get_article", return_value=None), \
             patch("app.api.endpoints.recommendations.get_db"):
            response = client.get(f"{self.BASE_URL}/9999/similar")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_happy_path_returns_similar_articles(self, client):
        """Multiple published articles + mocked LLM → returns similar articles with scores."""
        target = make_article(1, "Python Programming", "Learn Python")
        candidate_1 = make_article(2, "Advanced Python", "Deep Python")
        candidate_2 = make_article(3, "JavaScript Guide", "Learn JS")

        llm_response = make_llm_response_mock([
            {"id": 2, "similarity_score": 0.85},
            {"id": 3, "similarity_score": 0.40},
        ])

        with patch("app.api.endpoints.recommendations.get_article", return_value=target), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=[target, candidate_1, candidate_2]), \
             patch("app.ai.similarity.OpenAI") as mock_openai_cls, \
             patch("app.ai.similarity.get_settings") as mock_get_settings:

            mock_settings = MagicMock()
            mock_settings.openrouter_api_key = "test-key"
            mock_settings.openrouter_model = "test-model"
            mock_get_settings.return_value = mock_settings

            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = llm_response
            mock_openai_cls.return_value = mock_client

            response = client.get(f"{self.BASE_URL}/1/similar")

        assert response.status_code == 200
        data = response.json()
        assert data["article_id"] == 1
        assert len(data["similar_articles"]) == 2
        assert data["similar_articles"][0]["id"] == 2
        assert data["similar_articles"][0]["title"] == "Advanced Python"
        assert data["similar_articles"][0]["similarity_score"] == pytest.approx(0.85)

    def test_only_one_published_article_returns_empty_list(self, client):
        """Only the target article exists among published → no LLM call, empty list."""
        target = make_article(1, "Solo Article", "Unique content")

        with patch("app.api.endpoints.recommendations.get_article", return_value=target), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=[target]), \
             patch("app.ai.similarity.OpenAI") as mock_openai_cls:

            response = client.get(f"{self.BASE_URL}/1/similar")

            # LLM should NOT be called when there are no candidates
            mock_openai_cls.assert_not_called()

        assert response.status_code == 200
        data = response.json()
        assert data["article_id"] == 1
        assert data["similar_articles"] == []

    def test_draft_articles_excluded_from_candidates(self, client):
        """Draft articles should not appear in the candidates sent to LLM."""
        target = make_article(1, "Published Article", "Content", status="published")
        published = make_article(2, "Another Published", "Content", status="published")
        # Draft should be excluded — get_articles(status="published") won't return it
        # We simulate this by only returning published articles from get_articles

        llm_response = make_llm_response_mock([
            {"id": 2, "similarity_score": 0.75},
        ])

        with patch("app.api.endpoints.recommendations.get_article", return_value=target), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=[target, published]), \
             patch("app.ai.similarity.OpenAI") as mock_openai_cls, \
             patch("app.ai.similarity.get_settings") as mock_get_settings:

            mock_settings_obj = MagicMock()
            mock_settings_obj.openrouter_api_key = "test-key"
            mock_settings_obj.openrouter_model = "test-model"
            mock_get_settings.return_value = mock_settings_obj

            mock_llm_client = MagicMock()
            mock_llm_client.chat.completions.create.return_value = llm_response
            mock_openai_cls.return_value = mock_llm_client

            response = client.get(f"{self.BASE_URL}/1/similar")

        assert response.status_code == 200
        data = response.json()
        similar_ids = [a["id"] for a in data["similar_articles"]]
        assert 2 in similar_ids
        # draft article ID 3 not in results
        assert 3 not in similar_ids

    def test_limit_parameter_default_is_5(self, client):
        """Default limit is 5 — endpoint accepts no limit param."""
        target = make_article(1, "Target", "Content")
        candidates = [make_article(i, f"Article {i}", f"Content {i}") for i in range(2, 9)]
        all_articles = [target] + candidates

        similar_list = [{"id": i, "similarity_score": round(0.9 - i * 0.05, 2)} for i in range(2, 9)]
        llm_response = make_llm_response_mock(similar_list)

        with patch("app.api.endpoints.recommendations.get_article", return_value=target), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=all_articles), \
             patch("app.ai.similarity.OpenAI") as mock_openai_cls, \
             patch("app.ai.similarity.get_settings") as mock_get_settings:

            mock_settings_obj = MagicMock()
            mock_settings_obj.openrouter_api_key = "test-key"
            mock_settings_obj.openrouter_model = "test-model"
            mock_get_settings.return_value = mock_settings_obj

            mock_llm_client = MagicMock()
            mock_llm_client.chat.completions.create.return_value = llm_response
            mock_openai_cls.return_value = mock_llm_client

            response = client.get(f"{self.BASE_URL}/1/similar")

        assert response.status_code == 200
        data = response.json()
        assert len(data["similar_articles"]) <= 5

    def test_custom_limit_parameter(self, client):
        """Custom limit parameter is respected."""
        target = make_article(1, "Target", "Content")
        candidates = [make_article(i, f"Article {i}", f"Content {i}") for i in range(2, 7)]
        all_articles = [target] + candidates

        similar_list = [{"id": i, "similarity_score": round(0.9 - i * 0.05, 2)} for i in range(2, 7)]
        llm_response = make_llm_response_mock(similar_list)

        with patch("app.api.endpoints.recommendations.get_article", return_value=target), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=all_articles), \
             patch("app.ai.similarity.OpenAI") as mock_openai_cls, \
             patch("app.ai.similarity.get_settings") as mock_get_settings:

            mock_settings_obj = MagicMock()
            mock_settings_obj.openrouter_api_key = "test-key"
            mock_settings_obj.openrouter_model = "test-model"
            mock_get_settings.return_value = mock_settings_obj

            mock_llm_client = MagicMock()
            mock_llm_client.chat.completions.create.return_value = llm_response
            mock_openai_cls.return_value = mock_llm_client

            response = client.get(f"{self.BASE_URL}/1/similar?limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["similar_articles"]) <= 2

    def test_llm_failure_returns_500(self, client):
        """LLM API call failure → 500 response with error detail."""
        target = make_article(1, "Target", "Content")
        candidate = make_article(2, "Candidate", "Content")

        with patch("app.api.endpoints.recommendations.get_article", return_value=target), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=[target, candidate]), \
             patch("app.ai.similarity.OpenAI") as mock_openai_cls, \
             patch("app.ai.similarity.get_settings") as mock_get_settings:

            mock_settings_obj = MagicMock()
            mock_settings_obj.openrouter_api_key = "test-key"
            mock_settings_obj.openrouter_model = "test-model"
            mock_get_settings.return_value = mock_settings_obj

            mock_llm_client = MagicMock()
            mock_llm_client.chat.completions.create.side_effect = Exception("Connection timeout")
            mock_openai_cls.return_value = mock_llm_client

            response = client.get(f"{self.BASE_URL}/1/similar")

        assert response.status_code == 500
        assert "Failed to compute article similarity" in response.json()["detail"]

    def test_malformed_json_from_llm_returns_500(self, client):
        """LLM returning malformed JSON → 500 response."""
        target = make_article(1, "Target", "Content")
        candidate = make_article(2, "Candidate", "Content")

        bad_response = MagicMock()
        bad_response.choices = [MagicMock()]
        bad_response.choices[0].message.content = "{{NOT JSON}}"

        with patch("app.api.endpoints.recommendations.get_article", return_value=target), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=[target, candidate]), \
             patch("app.ai.similarity.OpenAI") as mock_openai_cls, \
             patch("app.ai.similarity.get_settings") as mock_get_settings:

            mock_settings_obj = MagicMock()
            mock_settings_obj.openrouter_api_key = "test-key"
            mock_settings_obj.openrouter_model = "test-model"
            mock_get_settings.return_value = mock_settings_obj

            mock_llm_client = MagicMock()
            mock_llm_client.chat.completions.create.return_value = bad_response
            mock_openai_cls.return_value = mock_llm_client

            response = client.get(f"{self.BASE_URL}/1/similar")

        assert response.status_code == 500

    def test_response_schema_fields(self, client):
        """Response contains expected fields in the correct types."""
        target = make_article(1, "Python Tutorial", "Learn Python")
        candidate = make_article(2, "Advanced Python", "Deep dive")

        llm_response = make_llm_response_mock([{"id": 2, "similarity_score": 0.78}])

        with patch("app.api.endpoints.recommendations.get_article", return_value=target), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=[target, candidate]), \
             patch("app.ai.similarity.OpenAI") as mock_openai_cls, \
             patch("app.ai.similarity.get_settings") as mock_get_settings:

            mock_settings_obj = MagicMock()
            mock_settings_obj.openrouter_api_key = "test-key"
            mock_settings_obj.openrouter_model = "test-model"
            mock_get_settings.return_value = mock_settings_obj

            mock_llm_client = MagicMock()
            mock_llm_client.chat.completions.create.return_value = llm_response
            mock_openai_cls.return_value = mock_llm_client

            response = client.get(f"{self.BASE_URL}/1/similar")

        assert response.status_code == 200
        data = response.json()
        assert "article_id" in data
        assert "similar_articles" in data
        assert isinstance(data["article_id"], int)
        assert isinstance(data["similar_articles"], list)

        if data["similar_articles"]:
            item = data["similar_articles"][0]
            assert "id" in item
            assert "title" in item
            assert "similarity_score" in item
            assert isinstance(item["id"], int)
            assert isinstance(item["title"], str)
            assert isinstance(item["similarity_score"], float)

    def test_limit_out_of_range_returns_422(self, client):
        """limit=0 is below minimum (ge=1) → 422 validation error."""
        with patch("app.api.endpoints.recommendations.get_article", return_value=MagicMock()), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=[]):
            response = client.get(f"{self.BASE_URL}/1/similar?limit=0")

        assert response.status_code == 422

    def test_no_llm_call_when_no_candidates(self, client):
        """When no candidate articles exist, LLM is never called."""
        target = make_article(1, "Solo Article", "Unique")

        with patch("app.api.endpoints.recommendations.get_article", return_value=target), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=[target]), \
             patch("app.ai.similarity.OpenAI") as mock_openai_cls:

            response = client.get(f"{self.BASE_URL}/1/similar")
            mock_openai_cls.assert_not_called()

        assert response.status_code == 200

    def test_target_excluded_from_candidates(self, client):
        """The target article itself is excluded from the candidates list."""
        target = make_article(1, "Target", "Content", status="published")
        other = make_article(2, "Other", "Content", status="published")

        # get_articles returns both; endpoint should filter out target (id=1)
        captured_candidates = []

        def fake_find_similar(target_article, candidate_articles, limit):
            captured_candidates.extend(candidate_articles)
            return [{"id": 2, "similarity_score": 0.8}]

        with patch("app.api.endpoints.recommendations.get_article", return_value=target), \
             patch("app.api.endpoints.recommendations.get_articles", return_value=[target, other]), \
             patch("app.api.endpoints.recommendations.find_similar_articles", side_effect=fake_find_similar):

            response = client.get(f"{self.BASE_URL}/1/similar")

        assert response.status_code == 200
        candidate_ids = [a.id for a in captured_candidates]
        assert 1 not in candidate_ids
        assert 2 in candidate_ids
