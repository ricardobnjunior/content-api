"""TF-IDF based category classifier for article suggestions."""

import logging
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def suggest_categories(
    article_text: str,
    categorized_articles: list[dict[str, Any]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Suggest categories for an article using TF-IDF and cosine similarity.

    Builds a TF-IDF matrix from all categorized articles, computes cosine
    similarity between the target article and each categorized article, then
    aggregates scores by category (taking the max similarity per category)
    and returns the top-N results.

    Args:
        article_text: Combined title and content of the target article.
        categorized_articles: List of dicts, each with keys:
            - ``text`` (str): Combined title + content of the categorized article.
            - ``category_id`` (int): The category's primary key.
            - ``category_name`` (str): The category's display name.
        limit: Maximum number of category suggestions to return.

    Returns:
        List of dicts sorted by confidence descending, each containing:
            - ``category_id`` (int)
            - ``category_name`` (str)
            - ``confidence`` (float) between 0.0 and 1.0.
        Returns an empty list if ``categorized_articles`` is empty.
    """
    if not categorized_articles:
        logger.debug("No categorized articles provided; returning empty suggestions.")
        return []

    corpus_texts = [entry["text"] for entry in categorized_articles]

    vectorizer = TfidfVectorizer(stop_words="english", min_df=1)

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus_texts)
    except ValueError as exc:
        logger.warning("TF-IDF vectorization failed: %s", exc)
        return []

    try:
        target_vector = vectorizer.transform([article_text])
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to transform target article text: %s", exc)
        return []

    similarities = cosine_similarity(target_vector, tfidf_matrix)[0]

    # Aggregate: take max similarity per category
    category_scores: dict[int, dict[str, Any]] = {}
    for score, entry in zip(similarities, categorized_articles):
        cat_id = entry["category_id"]
        if cat_id not in category_scores or score > category_scores[cat_id]["confidence"]:
            category_scores[cat_id] = {
                "category_id": cat_id,
                "category_name": entry["category_name"],
                "confidence": float(score),
            }

    sorted_suggestions = sorted(
        category_scores.values(),
        key=lambda x: x["confidence"],
        reverse=True,
    )

    return sorted_suggestions[:limit]
