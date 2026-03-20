"""LLM-based article similarity engine using OpenRouter API."""

import json
import logging
from typing import Any

from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a content similarity expert. Given a target article and a list of candidate articles, "
    "you must analyze their topics, themes, and content to determine similarity. "
    "Return a JSON object with the following structure:\n"
    '{"similar": [{"id": <article_id>, "similarity_score": <float between 0 and 1>}]}\n'
    "Include ALL candidates in the response, sorted by similarity_score descending. "
    "Only return valid JSON. Do not include any explanation or markdown formatting."
)


def _build_user_prompt(
    target_article: Any,
    candidate_articles: list[Any],
) -> str:
    """Build the user prompt for the LLM similarity request.

    Args:
        target_article: The article to find similarities for.
        candidate_articles: List of candidate articles to compare against.

    Returns:
        Formatted user prompt string.
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
        lines.append(f"[ID:{article.id}] Title: {article.title} | Content: {content_preview}")

    lines.append("")
    lines.append(
        "Rank all candidate articles by similarity to the target article "
        "and return the JSON response."
    )

    return "\n".join(lines)


def find_similar_articles(
    target_article: Any,
    candidate_articles: list[Any],
    limit: int = 5,
) -> list[dict]:
    """Find articles similar to the target using LLM analysis.

    Sends the target article and candidates to the LLM via OpenRouter API,
    receives similarity scores, and returns the top results sorted by score.

    Args:
        target_article: The article ORM object to find similarities for.
        candidate_articles: List of candidate article ORM objects to compare.
        limit: Maximum number of similar articles to return.

    Returns:
        List of dicts with keys ``id`` and ``similarity_score``, sorted
        descending by score, limited to ``limit`` items.

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

    user_prompt = _build_user_prompt(target_article, candidate_articles)

    try:
        response = client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
    except Exception as exc:
        logger.error("LLM API call failed: %s", exc)
        raise RuntimeError(f"LLM API call failed: {exc}") from exc

    raw_content = response.choices[0].message.content or ""
    logger.debug("LLM similarity response: %s", raw_content)

    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse LLM JSON response: %r", raw_content)
        raise ValueError(f"LLM returned malformed JSON: {exc}") from exc

    if "similar" not in parsed or not isinstance(parsed["similar"], list):
        logger.error("LLM response missing 'similar' key or wrong type: %r", parsed)
        raise ValueError("LLM response has unexpected structure")

    # Build a set of valid candidate IDs for validation
    valid_ids = {article.id for article in candidate_articles}

    results = []
    for item in parsed["similar"]:
        try:
            article_id = int(item["id"])
            score = float(item["similarity_score"])
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning("Skipping malformed similarity item %r: %s", item, exc)
            continue

        if article_id not in valid_ids:
            logger.warning("LLM returned unknown article ID %d, skipping", article_id)
            continue

        results.append({"id": article_id, "similarity_score": score})

    # Sort descending by similarity score and limit
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:limit]
