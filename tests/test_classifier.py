"""Tests for the AI classifier module."""

import json
from unittest.mock import MagicMock, patch

import pytest

from app.ai.classifier import classify_article


def make_mock_response(content: str):
    """Create a mock OpenAI API response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = content
    return mock_response


def test_classify_article_returns_suggestions():
    """Test that classify_article returns parsed suggestions."""
    mock_content = json.dumps({
        "suggestions": [
            {"category_name": "Technology", "confidence": 0.95},
            {"category_name": "Science", "confidence": 0.75},
        ]
    })

    with patch("app.ai.classifier.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = make_mock_response(mock_content)

        result = classify_article(
            title="New AI breakthrough",
            content="Scientists develop new neural network",
            category_names=["Technology", "Science", "Sports"],
        )

    assert len(result) == 2
    assert result[0]["category_name"] == "Technology"
    assert result[0]["confidence"] == 0.95
    assert result[1]["category_name"] == "Science"
    assert result[1]["confidence"] == 0.75


def test_classify_article_invalid_json_raises_value_error():
    """Test that invalid JSON from LLM raises ValueError."""
    with patch("app.ai.classifier.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = make_mock_response("not valid json")

        with pytest.raises(ValueError, match="LLM returned malformed JSON"):
            classify_article(
                title="Test",
                content="Test content",
                category_names=["Tech"],
            )


def test_classify_article_missing_suggestions_key_raises_value_error():
    """Test that missing 'suggestions' key raises ValueError."""
    mock_content = json.dumps({"result": []})

    with patch("app.ai.classifier.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = make_mock_response(mock_content)

        with pytest.raises(ValueError, match="LLM response missing 'suggestions' key"):
            classify_article(
                title="Test",
                content="Test content",
                category_names=["Tech"],
            )


def test_classify_article_filters_invalid_items():
    """Test that invalid suggestion items are filtered out."""
    mock_content = json.dumps({
        "suggestions": [
            {"category_name": "Technology", "confidence": 0.9},
            {"category_name": 123, "confidence": 0.8},  # invalid name
            {"category_name": "Science", "confidence": "high"},  # invalid confidence
            {"category_name": "Sports", "confidence": 0.7},
        ]
    })

    with patch("app.ai.classifier.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = make_mock_response(mock_content)

        result = classify_article(
            title="Test",
            content="Test content",
            category_names=["Technology", "Science", "Sports"],
        )

    assert len(result) == 2
    assert result[0]["category_name"] == "Technology"
    assert result[1]["category_name"] == "Sports"


def test_classify_article_empty_suggestions():
    """Test that empty suggestions list is returned correctly."""
    mock_content = json.dumps({"suggestions": []})

    with patch("app.ai.classifier.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = make_mock_response(mock_content)

        result = classify_article(
            title="Test",
            content="Test content",
            category_names=["Technology"],
        )

    assert result == []
