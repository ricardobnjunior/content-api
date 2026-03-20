"""LLM-based article category classifier using OpenRouter API."""

import json
import logging
from typing import TypedDict

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a content classifier. Given an article title and content, "
    "along with a list of available categories, your task is to suggest "
    "the most relevant categories for the article.\n\n"
    "You MUST respond with valid JSON only, in this exact format:\n"
    '{"suggestions": [{"category_name": "CategoryName", "confidence": 0.85}, ...]}\n\n'
    "Rules:\n"
    "- Only suggest categories from the provided list.\n"
    "- Confidence scores must be floats between 0.0 and 1.0.\n"
    "- Sort suggestions by confidence score in descending order.\n"
    "- Only include categories that are genuinely relevant (confidence > 0.3).\n"
    "- Return an empty suggestions list if no categories are relevant.\n"
    "- Do NOT include any text outside the JSON object."
)


class CategorySuggestion(TypedDict):
    """A single category suggestion from the LLM classifier.

    Attributes:
        category_name: The name of the suggested category.
        confidence: Confidence score between 0.0 and 1.0.
    """

    category_name: str
    confidence: float


def classify_article(
    title: str,
    content: str,
    category_names: list[str],
    limit: int = 3,
) -> list[CategorySuggestion]:
    """Classify an article into categories using an LLM via OpenRouter API.

    Sends the article title, content, and available category names to an LLM
    and returns a ranked list of category suggestions with confidence scores.

    Args:
        title: The article title.
        content: The article body content.
        category_names: List of available category names to classify into.
        limit: Maximum number of suggestions to return.

    Returns:
        A list of CategorySuggestion dicts sorted by confidence descending,
        limited to `limit` items.

    Raises:
        ValueError: If the LLM returns malformed JSON or unexpected structure.
        Exception: If the OpenRouter API call fails.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

    category_list_str = ", ".join(f'"{name}"' for name in category_names)
    user_message = (
        f"Article Title: {title}\n\n"
        f"Article Content:\n{content}\n\n"
        f"Available Categories: [{category_list_str}]\n\n"
        "Please classify this article and return JSON with the most relevant categories."
    )

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content
    if not raw_content:
        logger.warning("LLM returned empty content")
        return []

    parsed = json.loads(raw_content)

    if not isinstance(parsed, dict) or "suggestions" not in parsed:
        raise ValueError(
            f"LLM response missing 'suggestions' key. Got: {raw_content[:200]}"
        )

    suggestions = parsed["suggestions"]
    if not isinstance(suggestions, list):
        raise ValueError(
            f"'suggestions' must be a list. Got: {type(suggestions)}"
        )

    valid_suggestions: list[CategorySuggestion] = []
    category_names_set = set(category_names)

    for item in suggestions:
        if not isinstance(item, dict):
            continue
        cat_name = item.get("category_name", "")
        confidence = item.get("confidence", 0.0)
        if cat_name not in category_names_set:
            logger.warning("LLM suggested unknown category '%s', skipping", cat_name)
            continue
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))
        valid_suggestions.append(
            CategorySuggestion(category_name=cat_name, confidence=confidence)
        )

    valid_suggestions.sort(key=lambda x: x["confidence"], reverse=True)
    return valid_suggestions[:limit]
