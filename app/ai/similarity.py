"""LLM-based article similarity engine using OpenRouter API."""

import json
import logging
from typing import Any

from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert content similarity analyzer. "
    "Given a target article and a list of candidate articles, "
    "rank the candidates by their semantic similarity to the target. "
    "Return ONLY valid JSON in this exact format, with no additional text or markdown:\n"
    '{"similar": [{"id": <integer>, "similarity_score": <float between 0 and 1>}]}\n'
    "Sort results by similarity_score descending. "
    "Only include candidates that have meaningful similarity (score > 0.1). "
    "The 'id' must be the exact candidate ID provided."
)


def _build_user_message(target_article: Any, candidate_articles: list[Any]) -> str:
    """Build the user message for the LLM prompt.

    Args:
        target_article: The article to find similar articles for.
        candidate_articles: List of candidate articles to compare against.

    Returns:
        Formatted user message string.
    """
    target_content_preview = (target_article.content or "")[:500]
    lines = [
        "TARGET ARTICLE:",
        f"Title: {target_article.title}",
        f"Content: {target_content_preview}",
        "",
        "CANDIDATE ARTICLES:",
    ]
    for article in candidate_articles:
        content_preview = (article.content or "")[:200]
        lines.append(f"ID {article.id}: Title: {article.title} | Content: {content_preview}")

    lines.append("")
    lines.append(
        "Rank all candidates by similarity to the target article. "
        "Return JSON with the 'similar' array containing all candidates with scores."
    )
    return "\n".join(lines)


def find_similar_articles(
    target_article: Any,
    candidate_articles: list[Any],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Find articles similar to the target using LLM analysis.

    Calls the OpenRouter LLM API to rank candidate articles by semantic
    similarity to the target article, then returns the top results.

    Args:
        target_article: The article object to find similar articles for.
            Must have `id`, `title`, and `content` attributes.
        candidate_articles: List of article objects to compare against.
            Each must have `id`, `title`, and `content` attributes.
        limit: Maximum number of similar articles to return.

    Returns:
        List of dicts with keys `id` (int) and `similarity_score` (float),
        sorted by similarity_score descending, up to `limit` results.

    Raises:
        ValueError: If the LLM returns malformed or unparseable JSON.
        RuntimeError: If the LLM API call fails.
    """
    if not candidate_articles:
        return []

    settings = get_settings()
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

    user_message = _build_user_message(target_article, candidate_articles)

    try:
        response = client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,
        )
    except Exception as exc:
        logger.error("LLM API call failed: %s", exc)
        raise RuntimeError(f"LLM API call failed: {exc}") from exc

    raw_content = response.choices[0].message.content
    if not raw_content:
        raise ValueError("LLM returned empty response")

    try:
        parsed = json.loads(raw_content.strip())
    except json.JSONDecodeError as exc:
        logger.error("LLM returned malformed JSON: %r", raw_content)
        raise ValueError(f"LLM returned malformed JSON: {exc}") from exc

    similar_list = parsed.get("similar", [])
    if not isinstance(similar_list, list):
        raise ValueError("LLM response 'similar' field is not a list")

    # Build a set of valid candidate IDs for filtering
    valid_ids = {article.id for article in candidate_articles}

    # Validate and filter results
    results = []
    for item in similar_list:
        if not isinstance(item, dict):
            continue
        article_id = item.get("id")
        score = item.get("similarity_score")
        if article_id is None or score is None:
            continue
        if not isinstance(article_id, int) or not isinstance(score, (int, float)):
            continue
        if article_id not in valid_ids:
            continue
        results.append({"id": article_id, "similarity_score": float(score)})

    # Sort by similarity_score descending
    results.sort(key=lambda x: x["similarity_score"], reverse=True)

    return results[:limit]
