"""Tests for article search, filtering, and pagination."""

import pytest
from fastapi.testclient import TestClient

from app.models.article import Article, ArticleStatus
from app.models.category import Category


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_category(db_session, name: str) -> Category:
    """Create and return a persisted Category."""
    cat = Category(name=name)
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


def _make_article(
    db_session,
    title: str,
    body: str,
    author: str,
    status: ArticleStatus = ArticleStatus.draft,
    categories: list[Category] | None = None,
) -> Article:
    """Create and return a persisted Article."""
    article = Article(
        title=title,
        body=body,
        author=author,
        status=status,
        categories=categories or [],
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    return article


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def populated_db(db_session):
    """Populate the database with a diverse set of articles for filter tests.

    Returns:
        A dict with ``cat_science``, ``cat_tech``, and the created articles.
    """
    cat_science = _make_category(db_session, "Science")
    cat_tech = _make_category(db_session, "Technology")

    articles = [
        _make_article(
            db_session,
            title="Python Basics",
            body="Learn the fundamentals of Python programming.",
            author="Alice",
            status=ArticleStatus.published,
            categories=[cat_tech],
        ),
        _make_article(
            db_session,
            title="Advanced Python",
            body="Deep dive into decorators and metaclasses.",
            author="Alice",
            status=ArticleStatus.draft,
            categories=[cat_tech],
        ),
        _make_article(
            db_session,
            title="Quantum Physics Introduction",
            body="Exploring the fundamentals of quantum mechanics.",
            author="Bob",
            status=ArticleStatus.published,
            categories=[cat_science],
        ),
        _make_article(
            db_session,
            title="Machine Learning Overview",
            body="An overview of supervised and unsupervised learning.",
            author="Bob",
            status=ArticleStatus.draft,
            categories=[cat_science, cat_tech],
        ),
        _make_article(
            db_session,
            title="History of Science",
            body="From Newton to Einstein: the journey of discovery.",
            author="Carol",
            status=ArticleStatus.published,
            categories=[cat_science],
        ),
    ]

    return {
        "cat_science": cat_science,
        "cat_tech": cat_tech,
        "articles": articles,
    }


# ---------------------------------------------------------------------------
# Search tests
# ---------------------------------------------------------------------------


def test_search_by_title(client: TestClient, populated_db):
    """Search returns articles whose title contains the substring."""
    response = client.get("/api/v1/articles/", params={"search": "Python"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 2
    titles = {item["title"] for item in data["items"]}
    assert titles == {"Python Basics", "Advanced Python"}


def test_search_by_title_case_insensitive(client: TestClient, populated_db):
    """Title search is case-insensitive."""
    response = client.get("/api/v1/articles/", params={"search": "python"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 2


def test_search_by_body(client: TestClient, populated_db):
    """Search returns articles whose body contains the substring."""
    response = client.get("/api/v1/articles/", params={"search": "fundamentals"})
    assert response.status_code == 200
    data = response.json()
    # "Python Basics" body + "Quantum Physics Introduction" body both contain "fundamentals"
    assert data["meta"]["total"] == 2
    titles = {item["title"] for item in data["items"]}
    assert "Python Basics" in titles
    assert "Quantum Physics Introduction" in titles


def test_search_by_body_case_insensitive(client: TestClient, populated_db):
    """Body search is case-insensitive."""
    response = client.get("/api/v1/articles/", params={"search": "FUNDAMENTALS"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 2


# ---------------------------------------------------------------------------
# Status filter tests
# ---------------------------------------------------------------------------


def test_filter_by_status_published(client: TestClient, populated_db):
    """Filter by status=published returns only published articles."""
    response = client.get("/api/v1/articles/", params={"status": "published"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 3
    for item in data["items"]:
        assert item["status"] == "published"


def test_filter_by_status_draft(client: TestClient, populated_db):
    """Filter by status=draft returns only draft articles."""
    response = client.get("/api/v1/articles/", params={"status": "draft"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 2
    for item in data["items"]:
        assert item["status"] == "draft"


# ---------------------------------------------------------------------------
# Author filter tests
# ---------------------------------------------------------------------------


def test_filter_by_author_alice(client: TestClient, populated_db):
    """Filter by author=Alice returns only Alice's articles."""
    response = client.get("/api/v1/articles/", params={"author": "Alice"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 2
    for item in data["items"]:
        assert item["author"] == "Alice"


def test_filter_by_author_bob(client: TestClient, populated_db):
    """Filter by author=Bob returns only Bob's articles."""
    response = client.get("/api/v1/articles/", params={"author": "Bob"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 2
    for item in data["items"]:
        assert item["author"] == "Bob"


def test_filter_by_author_carol(client: TestClient, populated_db):
    """Filter by author=Carol returns only Carol's article."""
    response = client.get("/api/v1/articles/", params={"author": "Carol"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["author"] == "Carol"


# ---------------------------------------------------------------------------
# Category filter tests
# ---------------------------------------------------------------------------


def test_filter_by_category_id_tech(client: TestClient, populated_db):
    """Filter by tech category_id returns only tech articles."""
    cat_tech = populated_db["cat_tech"]
    response = client.get("/api/v1/articles/", params={"category_id": cat_tech.id})
    assert response.status_code == 200
    data = response.json()
    # Python Basics, Advanced Python, Machine Learning Overview are in tech
    assert data["meta"]["total"] == 3
    titles = {item["title"] for item in data["items"]}
    assert "Python Basics" in titles
    assert "Advanced Python" in titles
    assert "Machine Learning Overview" in titles


def test_filter_by_category_id_science(client: TestClient, populated_db):
    """Filter by science category_id returns only science articles."""
    cat_science = populated_db["cat_science"]
    response = client.get("/api/v1/articles/", params={"category_id": cat_science.id})
    assert response.status_code == 200
    data = response.json()
    # Quantum Physics, Machine Learning Overview, History of Science are in science
    assert data["meta"]["total"] == 3
    titles = {item["title"] for item in data["items"]}
    assert "Quantum Physics Introduction" in titles
    assert "Machine Learning Overview" in titles
    assert "History of Science" in titles


# ---------------------------------------------------------------------------
# Pagination tests
# ---------------------------------------------------------------------------


def test_pagination_page1(client: TestClient, populated_db):
    """Page 1 with per_page=2 returns the first 2 items."""
    response = client.get("/api/v1/articles/", params={"page": 1, "per_page": 2})
    assert response.status_code == 200
    data = response.json()
    meta = data["meta"]
    assert meta["total"] == 5
    assert meta["page"] == 1
    assert meta["per_page"] == 2
    assert meta["pages"] == 3  # ceil(5/2)
    assert len(data["items"]) == 2


def test_pagination_page2(client: TestClient, populated_db):
    """Page 2 with per_page=2 returns the next 2 items (different from page 1)."""
    response_p1 = client.get("/api/v1/articles/", params={"page": 1, "per_page": 2})
    response_p2 = client.get("/api/v1/articles/", params={"page": 2, "per_page": 2})
    assert response_p1.status_code == 200
    assert response_p2.status_code == 200

    data_p1 = response_p1.json()
    data_p2 = response_p2.json()

    ids_p1 = {item["id"] for item in data_p1["items"]}
    ids_p2 = {item["id"] for item in data_p2["items"]}

    # Pages must not overlap
    assert ids_p1.isdisjoint(ids_p2)

    meta = data_p2["meta"]
    assert meta["page"] == 2
    assert meta["total"] == 5
    assert len(data_p2["items"]) == 2


def test_pagination_last_page(client: TestClient, populated_db):
    """Last page returns remaining items (possibly fewer than per_page)."""
    response = client.get("/api/v1/articles/", params={"page": 3, "per_page": 2})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["meta"]["page"] == 3
    assert data["meta"]["pages"] == 3


def test_pagination_beyond_last_page(client: TestClient, populated_db):
    """Requesting a page beyond the last returns empty items."""
    response = client.get("/api/v1/articles/", params={"page": 99, "per_page": 20})
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["total"] == 5


# ---------------------------------------------------------------------------
# Combined filter tests
# ---------------------------------------------------------------------------


def test_combined_search_and_status(client: TestClient, populated_db):
    """Combined search + status returns only matching published articles."""
    response = client.get(
        "/api/v1/articles/", params={"search": "Python", "status": "published"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["title"] == "Python Basics"
    assert data["items"][0]["status"] == "published"


def test_combined_author_and_status(client: TestClient, populated_db):
    """Combined author + status filter returns correct subset."""
    response = client.get(
        "/api/v1/articles/", params={"author": "Bob", "status": "published"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["title"] == "Quantum Physics Introduction"


def test_combined_category_and_status(client: TestClient, populated_db):
    """Combined category_id + status filter returns correct subset."""
    cat_tech = populated_db["cat_tech"]
    response = client.get(
        "/api/v1/articles/",
        params={"category_id": cat_tech.id, "status": "published"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["title"] == "Python Basics"


# ---------------------------------------------------------------------------
# Empty results test
# ---------------------------------------------------------------------------


def test_empty_results(client: TestClient, populated_db):
    """No matches returns empty items list with total=0."""
    response = client.get(
        "/api/v1/articles/", params={"search": "zzznomatchxyz"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["total"] == 0
    assert data["meta"]["pages"] == 0


# ---------------------------------------------------------------------------
# Meta fields presence
# ---------------------------------------------------------------------------


def test_meta_fields_present(client: TestClient, populated_db):
    """Response always contains meta with required fields."""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    meta = data["meta"]
    assert "total" in meta
    assert "page" in meta
    assert "per_page" in meta
    assert "pages" in meta


def test_default_meta_values(client: TestClient, populated_db):
    """Default pagination meta reflects correct defaults."""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    meta = data["meta"]
    assert meta["page"] == 1
    assert meta["per_page"] == 20


# ---------------------------------------------------------------------------
# Validation error tests
# ---------------------------------------------------------------------------


def test_per_page_max_validation(client: TestClient):
    """per_page > 100 returns 422 Unprocessable Entity."""
    response = client.get("/api/v1/articles/", params={"per_page": 101})
    assert response.status_code == 422


def test_page_min_validation(client: TestClient):
    """page < 1 returns 422 Unprocessable Entity."""
    response = client.get("/api/v1/articles/", params={"page": 0})
    assert response.status_code == 422


def test_per_page_zero_validation(client: TestClient):
    """per_page=0 returns 422 Unprocessable Entity."""
    response = client.get("/api/v1/articles/", params={"per_page": 0})
    assert response.status_code == 422
