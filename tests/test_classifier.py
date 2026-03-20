import json
from unittest.mock import MagicMock, patch


def test_build_prompt_contains_title():
    from app.ai.classifier import build_prompt

    prompt = build_prompt("My Article", "Some content", ["Tech", "Sports"])
    assert "My Article" in prompt


def test_build_prompt_contains_content():
    from app.ai.classifier import build_prompt

    prompt = build_prompt("Title", "Unique content here", ["Tech", "Sports"])
    assert "Unique content here" in prompt


def test_build_prompt_contains_category_names():
    from app.ai.classifier import build_prompt

    prompt = build_prompt("Title", "Content", ["Alpha", "Beta", "Gamma"])
    assert "Alpha" in prompt
    assert "Beta" in prompt
    assert "Gamma" in prompt


def test_build_prompt_empty_categories():
    from app.ai.classifier import build_prompt

    prompt = build_prompt("Title", "Content", [])
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def _make_mock_response(suggestions: list) -> MagicMock:
    content = json.dumps({"suggestions": suggestions})
    mock_message = MagicMock()
    mock_message.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


def test_classify_article_returns_suggestions():
    from app.ai.classifier import classify_article

    categories = [{"id": 1, "name": "Tech"}, {"id": 2, "name": "Sports"}]
    suggestions = [
        {"category_id": 1, "category_name": "Tech", "confidence": 0.9},
        {"category_id": 2, "category_name": "Sports", "confidence": 0.5},
    ]
    mock_response = _make_mock_response(suggestions)

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = classify_article("Title", "Content", categories, limit=5)

    assert len(result) == 2
    assert result[0]["category_id"] == 1


def test_classify_article_respects_limit():
    from app.ai.classifier import classify_article

    categories = [
        {"id": 1, "name": "Tech"},
        {"id": 2, "name": "Sports"},
        {"id": 3, "name": "Health"},
    ]
    suggestions = [
        {"category_id": 1, "category_name": "Tech", "confidence": 0.9},
        {"category_id": 2, "category_name": "Sports", "confidence": 0.7},
        {"category_id": 3, "category_name": "Health", "confidence": 0.5},
    ]
    mock_response = _make_mock_response(suggestions)

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = classify_article("Title", "Content", categories, limit=2)

    assert len(result) <= 2


def test_classify_article_sorted_by_confidence():
    from app.ai.classifier import classify_article

    categories = [
        {"id": 1, "name": "Tech"},
        {"id": 2, "name": "Sports"},
        {"id": 3, "name": "Health"},
    ]
    suggestions = [
        {"category_id": 3, "category_name": "Health", "confidence": 0.4},
        {"category_id": 1, "category_name": "Tech", "confidence": 0.95},
        {"category_id": 2, "category_name": "Sports", "confidence": 0.7},
    ]
    mock_response = _make_mock_response(suggestions)

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = classify_article("Title", "Content", categories, limit=5)

    confidences = [r["confidence"] for r in result]
    assert confidences == sorted(confidences, reverse=True)


def test_classify_article_raises_runtime_error_on_api_failure():
    import pytest
    from app.ai.classifier import classify_article

    categories = [{"id": 1, "name": "Tech"}]

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_get_client.return_value = mock_client

        with pytest.raises(RuntimeError):
            classify_article("Title", "Content", categories, limit=3)


def test_classify_article_raises_value_error_on_malformed_json():
    import pytest
    from app.ai.classifier import classify_article

    categories = [{"id": 1, "name": "Tech"}]

    mock_message = MagicMock()
    mock_message.content = "this is not json at all"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        with pytest.raises(ValueError):
            classify_article("Title", "Content", categories, limit=3)


def test_classify_article_raises_value_error_on_missing_suggestions_key():
    import pytest
    from app.ai.classifier import classify_article

    categories = [{"id": 1, "name": "Tech"}]

    mock_message = MagicMock()
    mock_message.content = json.dumps({"results": []})
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        with pytest.raises(ValueError):
            classify_article("Title", "Content", categories, limit=3)


def test_classify_article_skips_invalid_items():
    from app.ai.classifier import classify_article

    categories = [{"id": 1, "name": "Tech"}, {"id": 2, "name": "Sports"}]
    suggestions = [
        {"category_id": 1, "category_name": "Tech", "confidence": 0.9},
        {"bad_key": "no good"},
        {"category_id": 2, "category_name": "Sports", "confidence": 0.5},
    ]
    mock_response = _make_mock_response(suggestions)

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = classify_article("Title", "Content", categories, limit=5)

    assert all("category_id" in r for r in result)
    assert len(result) == 2
