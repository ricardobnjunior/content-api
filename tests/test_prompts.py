"""Tests for app/ai/prompts.py — system prompt content."""


def test_system_prompt_is_string():
    """SYSTEM_PROMPT should be a non-empty string."""
    from app.ai.prompts import SYSTEM_PROMPT

    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT) > 0


def test_system_prompt_mentions_json():
    """SYSTEM_PROMPT should instruct the LLM to return JSON."""
    from app.ai.prompts import SYSTEM_PROMPT

    assert "JSON" in SYSTEM_PROMPT or "json" in SYSTEM_PROMPT.lower()


def test_system_prompt_mentions_confidence():
    """SYSTEM_PROMPT should mention confidence scores."""
    from app.ai.prompts import SYSTEM_PROMPT

    assert "confidence" in SYSTEM_PROMPT.lower()


def test_system_prompt_mentions_suggestions():
    """SYSTEM_PROMPT should mention 'suggestions' key."""
    from app.ai.prompts import SYSTEM_PROMPT

    assert "suggestions" in SYSTEM_PROMPT


def test_system_prompt_mentions_category_name():
    """SYSTEM_PROMPT should mention 'category_name'."""
    from app.ai.prompts import SYSTEM_PROMPT

    assert "category_name" in SYSTEM_PROMPT
