"""LLM-based category classifier using OpenRouter API."""

import json
import logging
from typing import TypedDict

from openai import OpenAI

from app.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class CategorySuggestion(TypedDict):
    """A single category suggestion from the LLM.

    Attributes:
        category_name: The name of the suggested category.
        confidence: Confidence score between 0.0 and 1.0.
    """

    category_name: str
    confidence: float


def suggest_categories(
    title: str,
    content: str,
    category_names: list[str],
    settings: object,
) -> list[CategorySuggestion]:
    """Suggest categories for an article using an LLM via OpenRouter API.

    Sends the article title, content, and list of available category names to
    the OpenRouter API and returns a ranked list of category suggestions with
    confidence scores.

    Args:
        title: The article title.
        content: The article body text.
        category_names: List of available category names to classify into.
        settings: Application settings object with ``openrouter_api_key`` and
            ``openrouter_model`` attributes.

    Returns:
        List of CategorySuggestion dicts sorted by confidence descending.
        Returns an empty list if ``category_names`` is empty or on any error.

    Raises:
        RuntimeError: If the LLM API call fails or returns unparseable JSON.
    """
    if not category_names:
        return []

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

    category_list = "\n".join(f"- {name}" for name in category_names)
    user_message = USER_PROMPT_TEMPLATE.format(
        title=title,
        content=content,
        category_list=category_list,
    )

    try:
        response = client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        logger.error("OpenRouter API call failed: %s", exc)
        raise RuntimeError(f"LLM API call failed: {exc}") from exc

    raw_content = response.choices[0].message.content
    if not raw_content:
        raise RuntimeError("LLM returned empty response content.")

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse LLM JSON response: %r — %s", raw_content, exc)
        raise RuntimeError(f"LLM returned malformed JSON: {exc}") from exc

    raw_suggestions = data.get("suggestions", [])
    if not isinstance(raw_suggestions, list):
        raise RuntimeError("LLM response 'suggestions' field is not a list.")

    suggestions: list[CategorySuggestion] = []
    for item in raw_suggestions:
        if not isinstance(item, dict):
            continue
        name = item.get("category_name")
        confidence = item.get("confidence")
        if not isinstance(name, str) or not isinstance(confidence, (int, float)):
            continue
        suggestions.append(
            CategorySuggestion(
                category_name=name,
                confidence=float(confidence),
            )
        )

    suggestions.sort(key=lambda s: s["confidence"], reverse=True)
    return suggestions
