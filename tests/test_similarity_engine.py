"""Tests for app/ai/similarity.py — LLM-based similarity engine."""

import os
import json
from unittest.mock import MagicMock, patch

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")


def make_article(article_id: int, title: str, content: str, status: str = "published"):
    """Create a mock article object."""
    article = MagicMock()
    article.id = article_id
    article.title = title
    article.content = content
    article.status = status
    return article


def make_llm_response(similar_list: list) -> MagicMock:
    """Create a mock LLM response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = json.dumps({"similar": similar_list})
    return response


@pytest.fixture
def mock_openai_client():
    """Patch OpenAI client used in similarity module."""
    with patch("app.ai.similarity.OpenAI") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_settings():
    """Patch get_settings in similarity module."""
    with patch("app.ai.similarity.get_settings") as mock_get:
        settings = MagicMock()
        settings.openrouter_api_key = "test-key"
        settings.openrouter_model = "test-model"
        mock_get.return_value = settings
        yield settings


class TestFindSimilarArticles:
    """Tests for find_similar_articles function."""

    def test_returns_empty_list_when_no_candidates(self, mock_settings):
        """No candidates → returns empty list without calling LLM."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        target = make_article(1, "Target", "Some content")
        result = find_similar_articles(target, [], limit=5)

        assert result == []

    def test_happy_path_returns_similar_articles(self, mock_openai_client, mock_settings):
        """Multiple candidates + LLM response → returns ranked results."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        target = make_article(1, "Python Tutorial", "Learn Python programming")
        candidates = [
            make_article(2, "Advanced Python", "Deep dive into Python"),
            make_article(3, "JavaScript Basics", "Learn JS"),
        ]

        mock_openai_client.chat.completions.create.return_value = make_llm_response([
            {"id": 2, "similarity_score": 0.92},
            {"id": 3, "similarity_score": 0.45},
        ])

        result = find_similar_articles(target, candidates, limit=5)

        assert len(result) == 2
        assert result[0]["id"] == 2
        assert result[0]["similarity_score"] == pytest.approx(0.92)
        assert result[1]["id"] == 3
        assert result[1]["similarity_score"] == pytest.approx(0.45)

    def test_limit_parameter_restricts_results(self, mock_openai_client, mock_settings):
        """limit parameter caps the number of returned results."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        target = make_article(1, "Target", "Content")
        candidates = [make_article(i, f"Article {i}", f"Content {i}") for i in range(2, 7)]

        mock_openai_client.chat.completions.create.return_value = make_llm_response([
            {"id": i, "similarity_score": round(1.0 - i * 0.1, 1)} for i in range(2, 7)
        ])

        result = find_similar_articles(target, candidates, limit=2)
        assert len(result) <= 2

    def test_results_sorted_by_score_descending(self, mock_openai_client, mock_settings):
        """Results are sorted by similarity_score descending."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        target = make_article(1, "Target", "Content")
        candidates = [
            make_article(2, "Article 2", "Content 2"),
            make_article(3, "Article 3", "Content 3"),
            make_article(4, "Article 4", "Content 4"),
        ]

        # LLM returns in non-sorted order
        mock_openai_client.chat.completions.create.return_value = make_llm_response([
            {"id": 4, "similarity_score": 0.3},
            {"id": 2, "similarity_score": 0.9},
            {"id": 3, "similarity_score": 0.6},
        ])

        result = find_similar_articles(target, candidates, limit=10)
        scores = [r["similarity_score"] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_malformed_json_raises_value_error(self, mock_openai_client, mock_settings):
        """LLM returning malformed JSON raises ValueError."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        target = make_article(1, "Target", "Content")
        candidates = [make_article(2, "Article 2", "Content 2")]

        bad_response = MagicMock()
        bad_response.choices = [MagicMock()]
        bad_response.choices[0].message.content = "NOT VALID JSON {{{"
        mock_openai_client.chat.completions.create.return_value = bad_response

        with pytest.raises(ValueError, match="malformed JSON"):
            find_similar_articles(target, candidates, limit=5)

    def test_llm_api_failure_raises_runtime_error(self, mock_openai_client, mock_settings):
        """LLM API call failure raises RuntimeError."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        target = make_article(1, "Target", "Content")
        candidates = [make_article(2, "Article 2", "Content 2")]

        mock_openai_client.chat.completions.create.side_effect = Exception("Connection refused")

        with pytest.raises(RuntimeError, match="LLM API call failed"):
            find_similar_articles(target, candidates, limit=5)

    def test_empty_llm_response_raises_value_error(self, mock_openai_client, mock_settings):
        """LLM returning empty content raises ValueError."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        target = make_article(1, "Target", "Content")
        candidates = [make_article(2, "Article 2", "Content 2")]

        empty_response = MagicMock()
        empty_response.choices = [MagicMock()]
        empty_response.choices[0].message.content = ""
        mock_openai_client.chat.completions.create.return_value = empty_response

        with pytest.raises(ValueError, match="empty response"):
            find_similar_articles(target, candidates, limit=5)

    def test_invalid_ids_filtered_out(self, mock_openai_client, mock_settings):
        """LLM returning IDs not in candidate list are filtered out."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        target = make_article(1, "Target", "Content")
        candidates = [make_article(2, "Article 2", "Content 2")]

        mock_openai_client.chat.completions.create.return_value = make_llm_response([
            {"id": 2, "similarity_score": 0.8},
            {"id": 999, "similarity_score": 0.95},  # invalid ID
        ])

        result = find_similar_articles(target, candidates, limit=5)
        ids = [r["id"] for r in result]
        assert 999 not in ids
        assert 2 in ids

    def test_missing_id_or_score_items_skipped(self, mock_openai_client, mock_settings):
        """Items missing 'id' or 'similarity_score' are skipped."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        target = make_article(1, "Target", "Content")
        candidates = [
            make_article(2, "Article 2", "Content 2"),
            make_article(3, "Article 3", "Content 3"),
        ]

        mock_openai_client.chat.completions.create.return_value = make_llm_response([
            {"id": 2, "similarity_score": 0.8},
            {"id": 3},  # missing score
            {"similarity_score": 0.5},  # missing id
        ])

        result = find_similar_articles(target, candidates, limit=5)
        assert len(result) == 1
        assert result[0]["id"] == 2

    def test_similar_not_list_raises_value_error(self, mock_openai_client, mock_settings):
        """LLM response with 'similar' not being a list raises ValueError."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        target = make_article(1, "Target", "Content")
        candidates = [make_article(2, "Article 2", "Content 2")]

        bad_response = MagicMock()
        bad_response.choices = [MagicMock()]
        bad_response.choices[0].message.content = json.dumps({"similar": "not-a-list"})
        mock_openai_client.chat.completions.create.return_value = bad_response

        with pytest.raises(ValueError, match="not a list"):
            find_similar_articles(target, candidates, limit=5)

    def test_content_preview_uses_first_200_chars_for_candidates(
        self, mock_openai_client, mock_settings
    ):
        """Builds user message correctly — candidate content truncated to 200 chars."""
        from app.ai.similarity import _build_user_message  # noqa: E402

        target = make_article(1, "Target", "Target content")
        long_content = "x" * 500
        candidate = make_article(2, "Article 2", long_content)

        message = _build_user_message(target, [candidate])

        # The candidate content preview should be at most 200 chars of 'x'
        assert "x" * 200 in message
        assert "x" * 201 not in message

    def test_target_content_preview_uses_first_500_chars(self, mock_settings):
        """Target article content is truncated to 500 chars in the prompt."""
        from app.ai.similarity import _build_user_message  # noqa: E402

        long_content = "y" * 600
        target = make_article(1, "Target", long_content)
        candidate = make_article(2, "Article 2", "Short content")

        message = _build_user_message(target, [candidate])

        assert "y" * 500 in message
        assert "y" * 501 not in message
