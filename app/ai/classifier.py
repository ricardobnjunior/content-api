"""LLM-based article category classifier using OpenRouter API."""

import json
import logging

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a content classifier. Given an article title, content, and a list of categories, "
    "identify which categories are most relevant to the article. "
    "Return ONLY a JSON object in this exact format: "
    '{\"suggestions\": [{\"category_name\": \"CategoryName\", \"confidence\": 0.85}, ...]}. '
    "Confidence must be a float between 0.0 and 1.0. "
    "Only include categories from the provided list. "
    "Return an empty suggestions array if no categories are relevant."
)


def classify_article(
    title: str,
    content: str,
    category_names: list[str],
) -> list[dict]:
    """Classify an article into relevant categories using an LLM via OpenRouter.

    Sends the article title, content, and list of available category names
    to the OpenRouter API and parses the returned JSON response into a list
    of category suggestion dicts with confidence scores.

    Args:
        title: The article title.
        content: The article body content.
        category_names: List of available category names to classify into.

    Returns:
        List of dicts, each with keys ``category_name`` (str) and
        ``confidence`` (float), sorted by confidence descending as returned
        by the LLM.

    Raises:
        ValueError: If the LLM response cannot be parsed as valid JSON or
            does not contain the expected ``suggestions`` key.
        Exception: If the OpenRouter API call fails for any reason.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

    categories_str = ", ".join(category_names)
    user_message = (
        "Article Title: {title}\n\n"
        "Article Content:\n{content}\n\n"
        "Available Categories: {categories}\n\n"
        "Classify this article into the most relevant categories from the list above."
    ).format(title=title, content=content, categories=categories_str)

    logger.debug("Calling OpenRouter API with model %s", settings.openrouter_model)

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content
    logger.debug("OpenRouter raw response: %s", raw_content)

    try:
        parsed = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(
            f"LLM returned malformed JSON: {raw_content!r}"
        ) from exc

    if "suggestions" not in parsed:
        raise ValueError(
            f"LLM response missing 'suggestions' key. Got: {parsed!r}"
        )

    suggestions = parsed["suggestions"]
    if not isinstance(suggestions, list):
        raise ValueError(
            f"LLM 'suggestions' is not a list. Got: {type(suggestions)!r}"
        )

    validated: list[dict] = []
    for item in suggestions:
        if not isinstance(item, dict):
            continue
        category_name = item.get("category_name")
        confidence = item.get("confidence")
        if not isinstance(category_name, str):
            continue
        if not isinstance(confidence, (int, float)):
            continue
        validated.append(
            {
                "category_name": category_name,
                "confidence": float(confidence),
            }
        )

    return validated
