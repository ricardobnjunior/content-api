"""Similarity engine for content-based article recommendations."""

import logging
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

MIN_SIMILARITY_SCORE = 0.1


@dataclass
class SimilarArticle:
    """Represents an article similar to the target article."""

    id: int
    title: str
    similarity_score: float


def _build_corpus_text(article) -> str:
    """Build a text corpus string from an article's title and content."""
    title = article.title or ""
    content = article.content or ""
    return f"{title} {content}".strip()


def find_similar_articles(
    db: Session,
    article_id: int,
    limit: int = 5,
) -> list:
    """Find articles similar to the given article using TF-IDF cosine similarity."""
    from app.models.article import Article

    published_articles = (
        db.query(Article)
        .filter(Article.status == "published")
        .all()
    )

    if len(published_articles) < 2:
        logger.info(
            "Not enough published articles (%d) to compute similarity.",
            len(published_articles),
        )
        return []

    corpus_articles = []
    corpus_texts = []
    target_index = None

    for idx, article in enumerate(published_articles):
        text = _build_corpus_text(article)
        corpus_articles.append(article)
        corpus_texts.append(text)
        if article.id == article_id:
            target_index = idx

    if target_index is None:
        logger.warning(
            "Article %d not found among published articles.", article_id
        )
        return []

    vectorizer = TfidfVectorizer(
        strip_accents="unicode",
        lowercase=True,
        analyzer="word",
        stop_words="english",
        min_df=1,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus_texts)
    except ValueError as exc:
        logger.error("TF-IDF vectorization failed: %s", exc)
        return []

    target_vector = tfidf_matrix[target_index]
    similarity_scores = cosine_similarity(target_vector, tfidf_matrix).flatten()

    results = []
    for idx, (article, score) in enumerate(zip(corpus_articles, similarity_scores)):
        if idx == target_index:
            continue
        if score < MIN_SIMILARITY_SCORE:
            continue
        results.append(
            SimilarArticle(
                id=article.id,
                title=article.title,
                similarity_score=float(score),
            )
        )

    results.sort(key=lambda x: x.similarity_score, reverse=True)
    return results[:limit]
