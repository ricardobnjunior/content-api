"""LLM-based article similarity engine using OpenRouter API."""

import json
import logging
from typing import Any

from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert content analyst. Your task is to analyze an article "
    "and determine how similar a list of candidate articles are to it.\n\n"
    "Return ONLY a JSON object (no markdown, no explanation) with this structure:\n"
    '{"similar": [{"id": <int>, "similarity_score": <float between 0 and 1>}]}\n\n'
    "Rules:\n"
    "- Include ALL candidate articles in the response with a score.\n"
    "- similarity_score must be a float between 0.0 (not similar) and 1.0 (identical topic).\n"
    "- Sort by similarity_score descending.\n"
    "- Do NOT include any text outside the JSON object."
)


def _build_user_message(target_article: Any, candidate_articles: list[Any]) -> str:
    """Build the user message for the LLM similarity request."""
    lines = [
        "TARGET ARTICLE:",
        f"Title: {target_article.title}",
        f"Content: {target_article.content}",
        "",
        "CANDIDATE ARTICLES:",
    ]
    for article in candidate_articles:
        content_preview = (article.content or "")[:200]
        lines.append(f"[{article.id}] Title: {article.title} | Content: {content_preview}")

    lines.append("")
    lines.append(
        "Rank ALL candidate articles by similarity to the target article "
        "and return the JSON response as specified."
    )
    return "\n".join(lines)


def get_similar_articles(
    target_article: Any,
    candidate_articles: list[Any],
    limit: int = 5,
    model: str | None = None,
) -> list[dict[str, Any]]:
    """Find articles similar to the target using an LLM via OpenRouter API."""
    settings = get_settings()
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

    selected_model = model or settings.openrouter_model
    user_message = _build_user_message(target_article, candidate_articles)

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
    except Exception as exc:
        logger.error("OpenRouter API call failed: %s", exc)
        raise RuntimeError(f"LLM API call failed: {exc}") from exc

    raw_content = response.choices[0].message.content or ""
    logger.debug("LLM similarity raw response: %s", raw_content)

    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned malformed JSON: %s", raw_content)
        raise ValueError(f"LLM returned malformed JSON: {exc}") from exc

    if "similar" not in parsed or not isinstance(parsed["similar"], list):
        raise ValueError(f"LLM response missing 'similar' list: {parsed}")

    # Validate and normalize each entry
    valid_candidate_ids = {article.id for article in candidate_articles}
    results: list[dict[str, Any]] = []
    for item in parsed["similar"]:
        if not isinstance(item, dict):
            continue
        article_id = item.get("id")
        score = item.get("similarity_score")
        if article_id is None or score is None:
            continue
        if not isinstance(article_id, int) or article_id not in valid_candidate_ids:
            continue
        try:
            score_float = float(score)
        except (TypeError, ValueError):
            continue
        # Clamp score to [0.0, 1.0]
        score_float = max(0.0, min(1.0, score_float))
        results.append({"id": article_id, "similarity_score": score_float})

    # Sort descending by similarity score and apply limit
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:limit]
