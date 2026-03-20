"""LLM-based category classifier using the OpenRouter API."""

import json
from typing import Any

from openai import OpenAI

from app.ai.prompts import SYSTEM_PROMPT
from app.config import settings


def build_prompt(title: str, content: str, category_names: list[str]) -> str:
    """Build the user prompt for the LLM classifier.

    Args:
        title: The article title.
        content: The article body content.
        category_names: List of available category names to classify against.

    Returns:
        str: Formatted prompt string for the LLM.
    """
    categories_str = ", ".join(category_names)
    return (
        f"Article Title: {title}\n\n"
        f"Article Content:\n{content}\n\n"
        f"Available Categories: {categories_str}\n\n"
        "Please classify this article and suggest the most relevant categories with confidence scores."
    )


def classify_article(
    title: str,
    content: str,
    category_names: list[str],
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Classify an article by suggesting relevant categories using an LLM.

    Sends the article title, content, and list of available category names to
    OpenRouter (OpenAI-compatible API). Parses the JSON response and returns
    the top-N suggestions sorted by confidence descending.

    Args:
        title: The article title.
        content: The article body content.
        category_names: List of existing category names in the database.
        limit: Maximum number of suggestions to return.

    Returns:
        list[dict]: List of dicts with keys ``category_name`` (str) and
        ``confidence`` (float), sorted by confidence descending, limited to
        ``limit`` items.

    Raises:
        ValueError: If the LLM returns malformed or unexpected JSON.
        RuntimeError: If the OpenRouter API call fails.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

    user_prompt = build_prompt(title, content, category_names)

    try:
        response = client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        raise RuntimeError(f"OpenRouter API call failed: {exc}") from exc

    raw_content = response.choices[0].message.content

    try:
        parsed = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"LLM returned malformed JSON: {raw_content!r}") from exc

    suggestions = parsed.get("suggestions")
    if not isinstance(suggestions, list):
        raise ValueError(f"LLM response missing 'suggestions' list: {parsed!r}")

    # Validate and normalise each suggestion entry
    valid_suggestions: list[dict[str, Any]] = []
    for item in suggestions:
        if not isinstance(item, dict):
            continue
        cat_name = item.get("category_name")
        confidence = item.get("confidence")
        if cat_name is None or confidence is None:
            continue
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            continue
        valid_suggestions.append({"category_name": str(cat_name), "confidence": confidence})

    # Sort by confidence descending and limit
    valid_suggestions.sort(key=lambda x: x["confidence"], reverse=True)
    return valid_suggestions[:limit]
