"""Tests for the LLM-based article category classifier."""

import json
from unittest.mock import MagicMock, patch

import pytest

from app.ai.classifier import classify_article, CategorySuggestion


def make_mock_response(content: str) -> MagicMock:
    """Helper to build a mock OpenAI response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = content
    return mock_response


@pytest.fixture
def mock_openai_client():
    """Patch the OpenAI client used inside classify_article."""
    with patch("app.ai.classifier.OpenAI") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance


def test_classify_article_happy_path(mock_openai_client):
    """Returns suggestions when LLM returns valid JSON."""
    llm_json = json.dumps({
        "suggestions": [
            {"category_name": "Technology", "confidence": 0.9},
            {"category_name": "Science", "confidence": 0.6},
        ]
    })
    mock_openai_client.chat.completions.create.return_value = make_mock_response(llm_json)

    result = classify_article(
        title="AI Advances",
        content="New breakthroughs in machine learning.",
        category_names=["Technology", "Science", "Sports"],
        limit=3,
    )

    assert len(result) == 2
    assert result[0]["category_name"] == "Technology"
    assert result[0]["confidence"] == pytest.approx(0.9)
    assert result[1]["category_name"] == "Science"
    assert result[1]["confidence"] == pytest.approx(0.6)


def test_classify_article_limit_applied(mock_openai_client):
    """Respects the limit parameter."""
    llm_json = json.dumps({
        "suggestions": [
            {"category_name": "Technology", "confidence": 0.9},
            {"category_name": "Science", "confidence": 0.7},
            {"category_name": "Sports", "confidence": 0.5},
        ]
    })
    mock_openai_client.chat.completions.create.return_value = make_mock_response(llm_json)

    result = classify_article(
        title="Mixed Article",
        content="Content here.",
        category_names=["Technology", "Science", "Sports"],
        limit=2,
    )

    assert len(result) == 2
    assert result[0]["category_name"] == "Technology"
    assert result[1]["category_name"] == "Science"


def test_classify_article_sorted_by_confidence(mock_openai_client):
    """Suggestions are sorted by confidence descending."""
    llm_json = json.dumps({
        "suggestions": [
            {"category_name": "Science", "confidence": 0.5},
            {"category_name": "Technology", "confidence": 0.95},
        ]
    })
    mock_openai_client.chat.completions.create.return_value = make_mock_response(llm_json)

    result = classify_article(
        title="Article",
        content="Content.",
        category_names=["Technology", "Science"],
        limit=3,
    )

    assert result[0]["confidence"] > result[1]["confidence"]
    assert result[0]["category_name"] == "Technology"


def test_classify_article_unknown_category_skipped(mock_openai_client):
    """LLM-suggested categories not in the input list are skipped."""
    llm_json = json.dumps({
        "suggestions": [
            {"category_name": "Technology", "confidence": 0.9},
            {"category_name": "FakeCategory", "confidence": 0.8},
        ]
    })
    mock_openai_client.chat.completions.create.return_value = make_mock_response(llm_json)

    result = classify_article(
        title="Tech Article",
        content="About tech.",
        category_names=["Technology", "Science"],
        limit=5,
    )

    names = [s["category_name"] for s in result]
    assert "FakeCategory" not in names
    assert "Technology" in names


def test_classify_article_empty_content_returns_empty(mock_openai_client):
    """Returns empty list when LLM returns empty suggestions."""
    llm_json = json.dumps({"suggestions": []})
    mock_openai_client.chat.completions.create.return_value = make_mock_response(llm_json)

    result = classify_article(
        title="Unknown",
        content="",
        category_names=["Technology"],
        limit=3,
    )

    assert result == []


def test_classify_article_empty_llm_content_returns_empty(mock_openai_client):
    """Returns empty list when LLM returns None/empty string."""
    mock_openai_client.chat.completions.create.return_value = make_mock_response("")

    result = classify_article(
        title="Article",
        content="Content.",
        category_names=["Technology"],
        limit=3,
    )

    assert result == []


def test_classify_article_malformed_json_raises(mock_openai_client):
    """Raises an error when LLM returns invalid JSON."""
    mock_openai_client.chat.completions.create.return_value = make_mock_response(
        "not valid json at all"
    )

    with pytest.raises(Exception):
        classify_article(
            title="Article",
            content="Content.",
            category_names=["Technology"],
            limit=3,
        )


def test_classify_article_missing_suggestions_key_raises(mock_openai_client):
    """Raises ValueError when LLM JSON is missing 'suggestions' key."""
    llm_json = json.dumps({"result": "something unexpected"})
    mock_openai_client.chat.completions.create.return_value = make_mock_response(llm_json)

    with pytest.raises(ValueError, match="suggestions"):
        classify_article(
            title="Article",
            content="Content.",
            category_names=["Technology"],
            limit=3,
        )


def test_classify_article_confidence_clamped(mock_openai_client):
    """Confidence values are clamped to [0.0, 1.0]."""
    llm_json = json.dumps({
        "suggestions": [
            {"category_name": "Technology", "confidence": 1.5},
            {"category_name": "Science", "confidence": -0.2},
        ]
    })
    mock_openai_client.chat.completions.create.return_value = make_mock_response(llm_json)

    result = classify_article(
        title="Article",
        content="Content.",
        category_names=["Technology", "Science"],
        limit=5,
    )

    for suggestion in result:
        assert 0.0 <= suggestion["confidence"] <= 1.0


def test_classify_article_api_failure_propagates(mock_openai_client):
    """Raises exception when OpenAI API call fails."""
    mock_openai_client.chat.completions.create.side_effect = Exception("API timeout")

    with pytest.raises(Exception, match="API timeout"):
        classify_article(
            title="Article",
            content="Content.",
            category_names=["Technology"],
            limit=3,
        )


def test_classify_article_non_dict_item_skipped(mock_openai_client):
    """Non-dict items in suggestions list are skipped gracefully."""
    llm_json = json.dumps({
        "suggestions": [
            "not a dict",
            {"category_name": "Technology", "confidence": 0.8},
        ]
    })
    mock_openai_client.chat.completions.create.return_value = make_mock_response(llm_json)

    result = classify_article(
        title="Article",
        content="Content.",
        category_names=["Technology"],
        limit=5,
    )

    assert len(result) == 1
    assert result[0]["category_name"] == "Technology"


def test_classify_article_invalid_confidence_defaults_to_zero(mock_openai_client):
    """Non-numeric confidence defaults to 0.0."""
    llm_json = json.dumps({
        "suggestions": [
            {"category_name": "Technology", "confidence": "high"},
        ]
    })
    mock_openai_client.chat.completions.create.return_value = make_mock_response(llm_json)

    result = classify_article(
        title="Article",
        content="Content.",
        category_names=["Technology"],
        limit=5,
    )

    assert len(result) == 1
    assert result[0]["confidence"] == 0.0
