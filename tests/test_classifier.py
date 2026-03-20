"""Tests for app/ml/classifier.py — suggest_categories function."""

import pytest

from app.ml.classifier import suggest_categories


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def make_entry(category_id: int, category_name: str, text: str) -> dict:
    """Build a categorized article entry dict."""
    return {
        "text": text,
        "category_id": category_id,
        "category_name": category_name,
    }


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_suggest_categories_returns_top_limit_results():
    """With enough categorized articles, returns at most `limit` suggestions."""
    entries = [
        make_entry(1, "Technology", "Python programming software development code"),
        make_entry(2, "Science", "biology chemistry physics lab experiment"),
        make_entry(3, "Sports", "football soccer basketball tournament match"),
        make_entry(4, "Politics", "election government parliament vote party"),
    ]
    article_text = "Python software development programming tutorial"
    results = suggest_categories(article_text, entries, limit=2)

    assert len(results) <= 2
    # Technology should rank highest for Python-related text
    assert results[0]["category_id"] == 1
    assert results[0]["category_name"] == "Technology"
    assert 0.0 <= results[0]["confidence"] <= 1.0


def test_suggest_categories_returns_all_when_fewer_than_limit():
    """Returns fewer items than limit when fewer categories exist."""
    entries = [
        make_entry(1, "Technology", "Python programming software"),
    ]
    article_text = "Python programming tutorial"
    results = suggest_categories(article_text, entries, limit=5)

    assert len(results) == 1
    assert results[0]["category_id"] == 1


def test_suggest_categories_confidence_sorted_descending():
    """Results must be sorted by confidence in descending order."""
    entries = [
        make_entry(1, "Technology", "Python programming software code"),
        make_entry(2, "Science", "chemistry atoms molecules experiment"),
        make_entry(3, "Sports", "football match soccer game player"),
    ]
    article_text = "Python code programming language"
    results = suggest_categories(article_text, entries, limit=3)

    confidences = [r["confidence"] for r in results]
    assert confidences == sorted(confidences, reverse=True)


def test_suggest_categories_result_structure():
    """Each result dict has required keys with correct types."""
    entries = [
        make_entry(10, "Tech", "software hardware computer device"),
    ]
    results = suggest_categories("computer hardware device", entries, limit=1)

    assert len(results) == 1
    r = results[0]
    assert isinstance(r["category_id"], int)
    assert isinstance(r["category_name"], str)
    assert isinstance(r["confidence"], float)


def test_suggest_categories_aggregates_max_per_category():
    """When multiple articles share a category, take the max similarity score."""
    # Two articles for category 1, one very similar and one very different
    entries = [
        make_entry(1, "Tech", "Python programming software"),
        make_entry(1, "Tech", "completely unrelated medieval history castle"),
        make_entry(2, "History", "medieval history ancient castle fortress"),
    ]
    article_text = "Python programming software tutorial"
    results = suggest_categories(article_text, entries, limit=2)

    # Category 1 should appear once (not twice)
    cat_ids = [r["category_id"] for r in results]
    assert len(cat_ids) == len(set(cat_ids)), "Each category should appear at most once"
    # Tech should rank first
    assert results[0]["category_id"] == 1


def test_suggest_categories_default_limit_is_three():
    """Default limit returns at most 3 suggestions."""
    entries = [
        make_entry(1, "A", "python programming code software"),
        make_entry(2, "B", "science biology chemistry lab"),
        make_entry(3, "C", "sports football soccer match"),
        make_entry(4, "D", "politics election government vote"),
        make_entry(5, "E", "food cooking recipe kitchen"),
    ]
    article_text = "python code programming"
    results = suggest_categories(article_text, entries)

    assert len(results) <= 3


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def test_suggest_categories_empty_input_returns_empty():
    """Empty categorized_articles list returns empty list immediately."""
    results = suggest_categories("some article text", [], limit=3)
    assert results == []


def test_suggest_categories_article_text_empty_string():
    """Empty article text still runs without error."""
    entries = [
        make_entry(1, "Tech", "Python software development"),
    ]
    # Should not raise; may return low/zero confidence
    results = suggest_categories("", entries, limit=3)
    assert isinstance(results, list)


def test_suggest_categories_limit_zero_returns_empty():
    """Limit of 0 returns empty list."""
    entries = [
        make_entry(1, "Tech", "Python software development programming"),
    ]
    results = suggest_categories("Python software", entries, limit=0)
    assert results == []


def test_suggest_categories_all_empty_corpus_texts():
    """Handles corpus of empty strings without crashing."""
    entries = [
        make_entry(1, "Tech", ""),
        make_entry(2, "Science", ""),
    ]
    # TF-IDF on empty strings may raise ValueError internally; should return []
    results = suggest_categories("python programming", entries, limit=3)
    assert isinstance(results, list)


def test_suggest_categories_confidence_between_0_and_1():
    """All confidence values are within [0, 1]."""
    entries = [
        make_entry(1, "Technology", "Python machine learning artificial intelligence"),
        make_entry(2, "Sports", "football basketball soccer tournament"),
        make_entry(3, "Cooking", "recipe ingredient kitchen oven bake"),
    ]
    article_text = "deep learning neural network model training"
    results = suggest_categories(article_text, entries, limit=3)

    for r in results:
        assert 0.0 <= r["confidence"] <= 1.0


def test_suggest_categories_single_entry_single_category():
    """Single categorized article returns single suggestion."""
    entries = [
        make_entry(42, "OnlyCategory", "machine learning deep neural network"),
    ]
    results = suggest_categories("neural network training", entries, limit=3)

    assert len(results) == 1
    assert results[0]["category_id"] == 42
    assert results[0]["category_name"] == "OnlyCategory"
