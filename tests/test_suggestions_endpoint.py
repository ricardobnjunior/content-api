"""Integration tests for GET /api/v1/suggestions/categories/{article_id}."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.endpoints.suggestions import router as suggestions_router
from app.database import get_db


# ---------------------------------------------------------------------------
# Helpers — build lightweight mock Article and Category objects
# ---------------------------------------------------------------------------

def make_mock_category(cat_id: int, name: str) -> MagicMock:
    cat = MagicMock()
    cat.id = cat_id
    cat.name = name
    return cat


def make_mock_article(
    art_id: int,
    title: str,
    content: str,
    categories: list | None = None,
) -> MagicMock:
    art = MagicMock()
    art.id = art_id
    art.title = title
    art.content = content
    art.categories = categories or []
    return art


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    """TestClient that overrides get_db with a mock session."""
    mock_db = MagicMock()

    def override_get_db():
        yield mock_db

    app = FastAPI()
    app.include_router(suggestions_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c, mock_db


# ---------------------------------------------------------------------------
# Helper to configure db.query chain for the endpoint
# ---------------------------------------------------------------------------

def setup_db_mock(mock_db, target_article, categorized_articles):
    """Wire up the mock db.query().filter().first() / .all() chain."""

    query_mock = MagicMock()
    mock_db.query.return_value = query_mock

    first_filter = MagicMock()
    query_mock.filter.return_value = first_filter
    first_filter.first.return_value = target_article

    # Chain for second query: .filter().filter().all()
    second_filter = MagicMock()
    third_filter = MagicMock()
    first_filter.filter.return_value = second_filter
    second_filter.filter.return_value = third_filter
    third_filter.all.return_value = categorized_articles


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_article_not_found_returns_404(client):
    """Non-existent article_id → 404."""
    test_client, mock_db = client

    # Make db.query().filter().first() return None
    query_mock = MagicMock()
    mock_db.query.return_value = query_mock
    filter_mock = MagicMock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = None

    response = test_client.get("/api/v1/suggestions/categories/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Article not found"


def test_no_categorized_articles_returns_empty_suggestions(client):
    """Article exists but no other categorized articles → empty suggestions."""
    test_client, mock_db = client

    target = make_mock_article(1, "Python Tutorial", "Learn Python programming", categories=[])
    setup_db_mock(mock_db, target, categorized_articles=[])

    response = test_client.get("/api/v1/suggestions/categories/1")

    assert response.status_code == 200
    data = response.json()
    assert data["article_id"] == 1
    assert data["suggestions"] == []


def test_categorized_articles_returns_suggestions(client):
    """Categorized articles exist → returns suggestions with confidence scores."""
    test_client, mock_db = client

    cat_tech = make_mock_category(1, "Technology")
    cat_science = make_mock_category(2, "Science")

    target = make_mock_article(
        10, "Python machine learning", "deep learning neural networks"
    )
    article_with_cat = make_mock_article(
        2,
        "Machine learning algorithms",
        "neural networks deep learning Python",
        categories=[cat_tech, cat_science],
    )

    setup_db_mock(mock_db, target, categorized_articles=[article_with_cat])

    response = test_client.get("/api/v1/suggestions/categories/10")

    assert response.status_code == 200
    data = response.json()
    assert data["article_id"] == 10
    assert isinstance(data["suggestions"], list)
    assert len(data["suggestions"]) > 0

    suggestion = data["suggestions"][0]
    assert "category_id" in suggestion
    assert "category_name" in suggestion
    assert "confidence" in suggestion
    assert isinstance(suggestion["confidence"], float)
    assert 0.0 <= suggestion["confidence"] <= 1.0


def test_default_limit_is_three(client):
    """Without explicit limit, at most 3 suggestions returned."""
    test_client, mock_db = client

    target = make_mock_article(1, "Python Tutorial", "programming code software")

    # Build 5 categories, each on a separate article
    categories_data = [
        (1, "Tech", "Python programming code software"),
        (2, "Science", "biology chemistry atoms molecules"),
        (3, "Sports", "football soccer basketball match"),
        (4, "Politics", "election government parliament vote"),
        (5, "Food", "recipe ingredient kitchen cooking"),
    ]
    categorized = []
    for cat_id, cat_name, text in categories_data:
        title, content = text.split(" ", 1)
        cat = make_mock_category(cat_id, cat_name)
        art = make_mock_article(cat_id + 100, title, content, categories=[cat])
        categorized.append(art)

    setup_db_mock(mock_db, target, categorized_articles=categorized)

    response = test_client.get("/api/v1/suggestions/categories/1")

    assert response.status_code == 200
    data = response.json()
    assert len(data["suggestions"]) <= 3


def test_custom_limit_parameter(client):
    """Explicit limit=1 returns at most 1 suggestion."""
    test_client, mock_db = client

    target = make_mock_article(1, "Python Tutorial", "programming software development")

    cat_tech = make_mock_category(1, "Technology")
    cat_sci = make_mock_category(2, "Science")
    art_a = make_mock_article(
        2, "Python code", "software development programming", categories=[cat_tech]
    )
    art_b = make_mock_article(
        3, "Biology lab", "chemistry atoms experiment", categories=[cat_sci]
    )

    setup_db_mock(mock_db, target, categorized_articles=[art_a, art_b])

    response = test_client.get("/api/v1/suggestions/categories/1?limit=1")

    assert response.status_code == 200
    data = response.json()
    assert len(data["suggestions"]) <= 1


def test_custom_limit_larger_than_categories(client):
    """limit=10 with only 2 categories returns at most 2 suggestions."""
    test_client, mock_db = client

    target = make_mock_article(5, "AI Research", "machine learning neural network")

    cat_a = make_mock_category(1, "AI")
    cat_b = make_mock_category(2, "Research")
    art = make_mock_article(
        6, "Deep learning", "neural network machine learning AI", categories=[cat_a, cat_b]
    )

    setup_db_mock(mock_db, target, categorized_articles=[art])

    response = test_client.get("/api/v1/suggestions/categories/5?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data["suggestions"]) <= 2


def test_response_schema_has_correct_fields(client):
    """Response matches SuggestionsResponse schema."""
    test_client, mock_db = client

    target = make_mock_article(3, "Science article", "physics chemistry experiment")
    cat = make_mock_category(7, "Physics")
    art = make_mock_article(
        4, "Quantum mechanics", "physics particles energy wave", categories=[cat]
    )

    setup_db_mock(mock_db, target, categorized_articles=[art])

    response = test_client.get("/api/v1/suggestions/categories/3")

    assert response.status_code == 200
    data = response.json()
    assert "article_id" in data
    assert "suggestions" in data
    assert data["article_id"] == 3

    if data["suggestions"]:
        s = data["suggestions"][0]
        assert set(s.keys()) == {"category_id", "category_name", "confidence"}


def test_suggestions_sorted_by_confidence_descending(client):
    """Suggestions come back in descending confidence order."""
    test_client, mock_db = client

    target = make_mock_article(1, "Python AI", "machine learning Python code")

    cat_tech = make_mock_category(1, "Technology")
    cat_food = make_mock_category(2, "Food")

    art_tech = make_mock_article(
        2, "Python programming", "machine learning code software Python",
        categories=[cat_tech]
    )
    art_food = make_mock_article(
        3, "Cooking recipes", "ingredient kitchen oven bake food",
        categories=[cat_food]
    )

    setup_db_mock(mock_db, target, categorized_articles=[art_tech, art_food])

    response = test_client.get("/api/v1/suggestions/categories/1?limit=3")

    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    confidences = [s["confidence"] for s in suggestions]
    assert confidences == sorted(confidences, reverse=True)


def test_article_with_no_content(client):
    """Article with None content is handled gracefully."""
    test_client, mock_db = client

    target = make_mock_article(1, "Untitled", None)
    setup_db_mock(mock_db, target, categorized_articles=[])

    response = test_client.get("/api/v1/suggestions/categories/1")

    assert response.status_code == 200
    assert response.json()["suggestions"] == []
