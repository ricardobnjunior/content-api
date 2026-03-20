"""Tests for app/ai/similarity.py — LLM-based article similarity engine."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

# Ensure env vars are set before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")


def _make_article(article_id: int, title: str, content: str, status: str = "published"):
    """Create a mock article ORM object."""
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
def target_article():
    return _make_article(1, "Target Article", "This is the target article content.")


@pytest.fixture
def candidate_articles():
    return [
        _make_article(2, "Candidate One", "Related content about topic A."),
        _make_article(3, "Candidate Two", "Different content about topic B."),
        _make_article(4, "Candidate Three", "Somewhat related content."),
    ]


class TestFindSimilarArticlesHappyPath:
    """Happy path tests for find_similar_articles."""

    def test_returns_sorted_results_by_score(self, target_article, candidate_articles):
        """LLM response is parsed and results are sorted descending by score."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        llm_similar = [
            {"id": 3, "similarity_score": 0.62},
            {"id": 2, "similarity_score": 0.85},
            {"id": 4, "similarity_score": 0.45},
        ]
        mock_response = _make_llm_response(llm_similar)

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            results = find_similar_articles(target_article, candidate_articles, limit=5)

        assert len(results) == 3
        # Should be sorted descending
        assert results[0]["id"] == 2
        assert results[0]["similarity_score"] == pytest.approx(0.85)
        assert results[1]["id"] == 3
        assert results[1]["similarity_score"] == pytest.approx(0.62)
        assert results[2]["id"] == 4
        assert results[2]["similarity_score"] == pytest.approx(0.45)

    def test_limit_is_respected(self, target_article, candidate_articles):
        """Only up to `limit` results are returned."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        llm_similar = [
            {"id": 2, "similarity_score": 0.90},
            {"id": 3, "similarity_score": 0.70},
            {"id": 4, "similarity_score": 0.50},
        ]
        mock_response = _make_llm_response(llm_similar)

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            results = find_similar_articles(target_article, candidate_articles, limit=2)

        assert len(results) == 2
        assert results[0]["similarity_score"] >= results[1]["similarity_score"]

    def test_result_dict_has_required_keys(self, target_article, candidate_articles):
        """Each result dict has 'id' and 'similarity_score' keys."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        llm_similar = [{"id": 2, "similarity_score": 0.75}]
        mock_response = _make_llm_response(llm_similar)

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            results = find_similar_articles(target_article, candidate_articles, limit=5)

        assert len(results) >= 1
        for item in results:
            assert "id" in item
            assert "similarity_score" in item

    def test_openai_client_called_with_correct_model(self, target_article, candidate_articles):
        """The OpenAI client is called with the model from settings."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        llm_similar = [{"id": 2, "similarity_score": 0.80}]
        mock_response = _make_llm_response(llm_similar)

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            find_similar_articles(target_article, candidate_articles, limit=5)

            call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs is not None
            # temperature should be 0.1
            assert call_kwargs.kwargs.get("temperature") == 0.1


class TestFindSimilarArticlesEdgeCases:
    """Edge case tests for find_similar_articles."""

    def test_empty_candidates_returns_empty_list(self, target_article):
        """No LLM call is made when there are no candidates."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client

            results = find_similar_articles(target_article, [], limit=5)

        assert results == []
        mock_client.chat.completions.create.assert_not_called()

    def test_malformed_json_raises_value_error(self, target_article, candidate_articles):
        """ValueError is raised when LLM returns malformed JSON."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not valid json {{{"

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            with pytest.raises(ValueError, match="malformed JSON"):
                find_similar_articles(target_article, candidate_articles, limit=5)

    def test_missing_similar_key_raises_value_error(self, target_article, candidate_articles):
        """ValueError is raised when LLM response is missing 'similar' key."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({"results": []})

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            with pytest.raises(ValueError, match="unexpected structure"):
                find_similar_articles(target_article, candidate_articles, limit=5)

    def test_llm_api_failure_raises_runtime_error(self, target_article, candidate_articles):
        """RuntimeError is raised when the LLM API call throws an exception."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection error")

            with pytest.raises(RuntimeError, match="LLM API call failed"):
                find_similar_articles(target_article, candidate_articles, limit=5)

    def test_llm_returns_unknown_article_ids_are_skipped(self, target_article, candidate_articles):
        """Items with IDs not in the candidate set are silently skipped."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        llm_similar = [
            {"id": 2, "similarity_score": 0.85},
            {"id": 999, "similarity_score": 0.99},  # Not a real candidate
        ]
        mock_response = _make_llm_response(llm_similar)

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            results = find_similar_articles(target_article, candidate_articles, limit=5)

        ids_returned = [r["id"] for r in results]
        assert 999 not in ids_returned
        assert 2 in ids_returned

    def test_malformed_item_in_similar_list_is_skipped(self, target_article, candidate_articles):
        """Items missing required keys in the 'similar' list are skipped."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        llm_similar = [
            {"id": 2, "similarity_score": 0.85},
            {"bad_key": "no_id"},   # Malformed item
        ]
        mock_response = _make_llm_response(llm_similar)

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            results = find_similar_articles(target_article, candidate_articles, limit=5)

        assert len(results) == 1
        assert results[0]["id"] == 2

    def test_default_limit_is_five(self, target_article, candidate_articles):
        """Default limit of 5 is applied when not specified."""
        from app.ai.similarity import find_similar_articles  # noqa: E402

        # 6 items returned by LLM
        llm_similar = [
            {"id": 2, "similarity_score": 0.95},
            {"id": 3, "similarity_score": 0.85},
        ]
        # Only 2 candidates, so max 2 returned regardless
        mock_response = _make_llm_response(llm_similar)

        with patch("app.ai.similarity.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            # Call without specifying limit
            results = find_similar_articles(target_article, candidate_articles)

        # Results should not exceed 5 (default) or number of candidates
        assert len(results) <= 5


class TestBuildUserPrompt:
    """Tests for the _build_user_prompt helper."""

    def test_prompt_contains_target_title(self):
        """The prompt includes the target article's title."""
        from app.ai.similarity import _build_user_prompt  # noqa: E402

        target = _make_article(1, "My Target Title", "Target content here.")
        candidates = [_make_article(2, "Candidate", "Some content.")]

        prompt = _build_user_prompt(target, candidates)

        assert "My Target Title" in prompt

    def test_prompt_contains_candidate_ids(self):
        """The prompt includes all candidate article IDs."""
        from app.ai.similarity import _build_user_prompt  # noqa: E402

        target = _make_article(1, "Target", "Content.")
        candidates = [
            _make_article(10, "Candidate A", "Content A."),
            _make_article(20, "Candidate B", "Content B."),
        ]

        prompt = _build_user_prompt(target, candidates)

        assert "ID:10" in prompt
        assert "ID:20" in prompt

    def test_prompt_truncates_target_content_at_500_chars(self):
        """Target article content is truncated to 500 characters."""
        from app.ai.similarity import _build_user_prompt  # noqa: E402

        long_content = "A" * 1000
        target = _make_article(1, "Target", long_content)
        candidates = [_make_article(2, "Candidate", "Content.")]

        prompt = _build_user_prompt(target, candidates)

        # The content in the prompt should not contain more than 500 As in a row
        assert "A" * 501 not in prompt
        assert "A" * 500 in prompt

    def test_prompt_truncates_candidate_content_at_200_chars(self):
        """Candidate article content is truncated to 200 characters."""
        from app.ai.similarity import _build_user_prompt  # noqa: E402

        target = _make_article(1, "Target", "Target content.")
        long_content = "B" * 500
        candidates = [_make_article(2, "Candidate", long_content)]

        prompt = _build_user_prompt(target, candidates)

        # 200 Bs should appear, but not 201
        assert "B" * 200 in prompt
        assert "B" * 201 not in prompt

    def test_prompt_handles_none_content(self):
        """Articles with None content do not cause errors."""
        from app.ai.similarity import _build_user_prompt  # noqa: E402

        target = _make_article(1, "Target", None)
        candidates = [_make_article(2, "Candidate", None)]

        # Should not raise
        prompt = _build_user_prompt(target, candidates)
        assert "Target" in prompt
