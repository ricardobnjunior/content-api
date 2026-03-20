"""Tests for article search, filtering, and pagination."""

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models.article import Article, ArticleStatus
from app.models.category import Category


@pytest.fixture(autouse=True)
def clean_db():
    """Create tables and clean up after each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture()
def client():
    """Return a TestClient for the app."""
    return TestClient(app)


@pytest.fixture()
def db_session():
    """Provide a database session for test setup."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _create_category(db, name: str, slug: str) -> Category:
    """Helper to create a category."""
    cat = Category(name=name, slug=slug)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def _create_article(
    db,
    title: str,
    body: str,
    author: str,
    status: ArticleStatus = ArticleStatus.draft,
    categories: list = None,
) -> Article:
    """Helper to create an article."""
    article = Article(
        title=title,
        body=body,
        author=author,
        status=status,
        categories=categories or [],
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@pytest.fixture()
def sample_data(db_session):
    """Create a set of articles and categories for tests."""
    cat_tech = _create_category(db_session, "Technology", "technology")
    cat_science = _create_category(db_session, "Science", "science")

    a1 = _create_article(
        db_session,
        title="Python Programming Guide",
        body="Learn Python basics and advanced features.",
        author="Alice",
        status=ArticleStatus.published,
        categories=[cat_tech],
    )
    a2 = _create_article(
        db_session,
        title="Introduction to FastAPI",
        body="FastAPI is a modern web framework.",
        author="Bob",
        status=ArticleStatus.published,
        categories=[cat_tech],
    )
    a3 = _create_article(
        db_session,
        title="Draft Article on Biology",
        body="This article covers cell biology topics.",
        author="Alice",
        status=ArticleStatus.draft,
        categories=[cat_science],
    )
    a4 = _create_article(
        db_session,
        title="Space Exploration",
        body="Humanity reaches for the stars.",
        author="Carol",
        status=ArticleStatus.published,
        categories=[cat_science],
    )
    a5 = _create_article(
        db_session,
        title="Machine Learning Overview",
        body="Python is widely used in machine learning.",
        author="Bob",
        status=ArticleStatus.draft,
        categories=[cat_tech, cat_science],
    )

    return {
        "articles": [a1, a2, a3, a4, a5],
        "categories": [cat_tech, cat_science],
    }


# ---------------------------------------------------------------------------
# Search tests
# ---------------------------------------------------------------------------


def test_search_by_title_substring(client, sample_data):
    """Search by a word in the title returns matching articles."""
    response = client.get("/api/v1/articles/?search=Python")
    assert response.status_code == 200
    data = response.json()
    titles = [item["title"] for item in data["items"]]
    assert "Python Programming Guide" in titles
    assert data["meta"]["total"] >= 1
    for item in data["items"]:
        assert "python" in item["title"].lower() or "python" in item["body"].lower()


def test_search_by_body_substring(client, sample_data):
    """Search by a word found only in body returns matching articles."""
    response = client.get("/api/v1/articles/?search=stars")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["title"] == "Space Exploration"


def test_search_case_insensitive(client, sample_data):
    """Search is case-insensitive (ilike)."""
    response_lower = client.get("/api/v1/articles/?search=python")
    response_upper = client.get("/api/v1/articles/?search=PYTHON")
    response_mixed = client.get("/api/v1/articles/?search=PyThOn")

    assert response_lower.status_code == 200
    assert response_upper.status_code == 200
    assert response_mixed.status_code == 200

    total_lower = response_lower.json()["meta"]["total"]
    total_upper = response_upper.json()["meta"]["total"]
    total_mixed = response_mixed.json()["meta"]["total"]

    assert total_lower == total_upper == total_mixed
    assert total_lower > 0


def test_filter_by_status_draft(client, sample_data):
    """Filter by status=draft returns only draft articles."""
    response = client.get("/api/v1/articles/?status=draft")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 2
    for item in data["items"]:
        assert item["status"] == "draft"


def test_filter_by_status_published(client, sample_data):
    """Filter by status=published returns only published articles."""
    response = client.get("/api/v1/articles/?status=published")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 3
    for item in data["items"]:
        assert item["status"] == "published"


def test_filter_by_author(client, sample_data):
    """Filter by author returns only articles by that author."""
    response = client.get("/api/v1/articles/?author=Alice")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 2
    for item in data["items"]:
        assert item["author"] == "Alice"


def test_filter_by_author_bob(client, sample_data):
    """Filter by author=Bob returns only Bob's articles."""
    response = client.get("/api/v1/articles/?author=Bob")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 2
    for item in data["items"]:
        assert item["author"] == "Bob"


def test_filter_by_category_id(client, sample_data):
    """Filter by category_id returns only articles in that category."""
    cat_tech = sample_data["categories"][0]
    response = client.get(f"/api/v1/articles/?category_id={cat_tech.id}")
    assert response.status_code == 200
    data = response.json()
    # tech category has articles a1, a2, a5 = 3 articles
    assert data["meta"]["total"] == 3
    for item in data["items"]:
        cat_names = [c["name"] for c in item["categories"]]
        assert "Technology" in cat_names


def test_filter_by_category_id_science(client, sample_data):
    """Filter by science category returns correct articles."""
    cat_science = sample_data["categories"][1]
    response = client.get(f"/api/v1/articles/?category_id={cat_science.id}")
    assert response.status_code == 200
    data = response.json()
    # science category has a3, a4, a5 = 3 articles
    assert data["meta"]["total"] == 3


# ---------------------------------------------------------------------------
# Pagination tests
# ---------------------------------------------------------------------------


def test_pagination_page1(client, sample_data):
    """Page 1 with per_page=2 returns first 2 items."""
    response = client.get("/api/v1/articles/?page=1&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["meta"]["page"] == 1
    assert data["meta"]["per_page"] == 2
    assert data["meta"]["total"] == 5


def test_pagination_page2(client, sample_data):
    """Page 2 with per_page=2 returns next 2 items (no overlap with page 1)."""
    response_p1 = client.get("/api/v1/articles/?page=1&per_page=2")
    response_p2 = client.get("/api/v1/articles/?page=2&per_page=2")

    assert response_p1.status_code == 200
    assert response_p2.status_code == 200

    ids_p1 = {item["id"] for item in response_p1.json()["items"]}
    ids_p2 = {item["id"] for item in response_p2.json()["items"]}

    assert ids_p1.isdisjoint(ids_p2)
    assert len(ids_p2) == 2
    assert response_p2.json()["meta"]["page"] == 2


def test_pagination_page3_partial(client, sample_data):
    """Page 3 with per_page=2 returns the remaining 1 item (5 total)."""
    response = client.get("/api/v1/articles/?page=3&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["meta"]["page"] == 3
    assert data["meta"]["total"] == 5


def test_pagination_meta_fields(client, sample_data):
    """Verify all pagination meta fields are correct."""
    response = client.get("/api/v1/articles/?page=2&per_page=2")
    assert response.status_code == 200
    meta = response.json()["meta"]
    assert meta["total"] == 5
    assert meta["page"] == 2
    assert meta["per_page"] == 2
    # ceil(5 / 2) = 3
    assert meta["pages"] == 3


def test_per_page_limit(client, sample_data):
    """per_page limits the number of returned items."""
    response = client.get("/api/v1/articles/?per_page=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["meta"]["per_page"] == 1
    assert data["meta"]["total"] == 5
    assert data["meta"]["pages"] == 5


def test_per_page_max(client, sample_data):
    """per_page=100 (max) is accepted and returns all items when fewer than 100."""
    response = client.get("/api/v1/articles/?per_page=100")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 5
    assert len(data["items"]) == 5


def test_invalid_page_zero_returns_422(client, sample_data):
    """page=0 is rejected with 422."""
    response = client.get("/api/v1/articles/?page=0")
    assert response.status_code == 422


def test_invalid_per_page_zero_returns_422(client, sample_data):
    """per_page=0 is rejected with 422."""
    response = client.get("/api/v1/articles/?per_page=0")
    assert response.status_code == 422


def test_invalid_per_page_over_max_returns_422(client, sample_data):
    """per_page=101 exceeds maximum and is rejected with 422."""
    response = client.get("/api/v1/articles/?per_page=101")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Combined filter tests
# ---------------------------------------------------------------------------


def test_combined_search_and_status(client, sample_data):
    """Combining search and status filters returns only matching articles."""
    # Python appears in a1 (published) and a5 (draft)
    response = client.get("/api/v1/articles/?search=Python&status=published")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["status"] == "published"
        assert "python" in item["title"].lower() or "python" in item["body"].lower()
    # a1 matches (Python in title, published); a5 does NOT match (draft)
    assert data["meta"]["total"] == 1


def test_combined_author_and_status(client, sample_data):
    """Combining author and status filters narrows down results."""
    response = client.get("/api/v1/articles/?author=Alice&status=published")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["author"] == "Alice"
    assert data["items"][0]["status"] == "published"


def test_combined_author_and_category(client, sample_data):
    """Combining author and category_id filters works correctly."""
    cat_tech = sample_data["categories"][0]
    # Alice has: a1 (tech, published), a3 (science, draft)
    response = client.get(f"/api/v1/articles/?author=Alice&category_id={cat_tech.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["author"] == "Alice"


def test_combined_search_category_and_status(client, sample_data):
    """Three filters combined work correctly."""
    cat_tech = sample_data["categories"][0]
    # Published tech articles containing "FastAPI"
    response = client.get(
        f"/api/v1/articles/?search=FastAPI&status=published&category_id={cat_tech.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["title"] == "Introduction to FastAPI"


# ---------------------------------------------------------------------------
# Empty results tests
# ---------------------------------------------------------------------------


def test_empty_results_no_match(client, sample_data):
    """A search that matches nothing returns empty list with valid meta."""
    response = client.get("/api/v1/articles/?search=xyznonexistent12345")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["total"] == 0
    assert data["meta"]["pages"] == 0
    assert data["meta"]["page"] == 1


def test_empty_results_author_no_match(client, sample_data):
    """Filtering by unknown author returns empty results."""
    response = client.get("/api/v1/articles/?author=NonExistentAuthor")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["total"] == 0


def test_empty_results_category_no_match(client, sample_data):
    """Filtering by non-existent category_id returns empty results."""
    response = client.get("/api/v1/articles/?category_id=99999")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["total"] == 0


def test_no_filters_returns_all(client, sample_data):
    """No filters returns all articles."""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 5
    assert len(data["items"]) == 5


def test_response_structure(client, sample_data):
    """Response always contains 'items' and 'meta' with required fields."""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "meta" in data
    meta = data["meta"]
    assert "total" in meta
    assert "page" in meta
    assert "per_page" in meta
    assert "pages" in meta


# ---------------------------------------------------------------------------
# Unit tests for CRUD layer directly
# ---------------------------------------------------------------------------


def test_get_articles_no_filters(db_session, clean_db):
    """get_articles() with no filters returns all articles and total count."""
    from app.crud.article import get_articles

    _create_article(db_session, "Title A", "Body A", "Author A", ArticleStatus.draft)
    _create_article(db_session, "Title B", "Body B", "Author B", ArticleStatus.published)

    articles, total = get_articles(db_session)
    assert total == 2
    assert len(articles) == 2


def test_get_articles_search_filter(db_session, clean_db):
    """get_articles() search filters correctly on title and body."""
    from app.crud.article import get_articles

    _create_article(db_session, "Unique Title", "Common body text", "Author A", ArticleStatus.draft)
    _create_article(db_session, "Another Title", "Unique body content", "Author B", ArticleStatus.draft)
    _create_article(db_session, "No match here", "Nothing special", "Author C", ArticleStatus.draft)

    articles, total = get_articles(db_session, search="Unique")
    assert total == 2


def test_get_articles_status_filter(db_session, clean_db):
    """get_articles() status filter returns only matching status."""
    from app.crud.article import get_articles

    _create_article(db_session, "Draft One", "Body", "Author", ArticleStatus.draft)
    _create_article(db_session, "Draft Two", "Body", "Author", ArticleStatus.draft)
    _create_article(db_session, "Published One", "Body", "Author", ArticleStatus.published)

    articles, total = get_articles(db_session, status=ArticleStatus.draft)
    assert total == 2
    assert all(a.status == ArticleStatus.draft for a in articles)


def test_get_articles_author_filter(db_session, clean_db):
    """get_articles() author filter returns only matching author."""
    from app.crud.article import get_articles

    _create_article(db_session, "Article 1", "Body", "Alice", ArticleStatus.draft)
    _create_article(db_session, "Article 2", "Body", "Bob", ArticleStatus.draft)
    _create_article(db_session, "Article 3", "Body", "Alice", ArticleStatus.published)

    articles, total = get_articles(db_session, author="Alice")
    assert total == 2
    assert all(a.author == "Alice" for a in articles)


def test_get_articles_pagination(db_session, clean_db):
    """get_articles() pagination returns correct slice."""
    from app.crud.article import get_articles

    for i in range(5):
        _create_article(db_session, f"Title {i}", "Body", "Author", ArticleStatus.draft)

    articles_p1, total = get_articles(db_session, page=1, per_page=2)
    articles_p2, _ = get_articles(db_session, page=2, per_page=2)

    assert total == 5
    assert len(articles_p1) == 2
    assert len(articles_p2) == 2
    ids_p1 = {a.id for a in articles_p1}
    ids_p2 = {a.id for a in articles_p2}
    assert ids_p1.isdisjoint(ids_p2)


def test_get_articles_category_filter(db_session, clean_db):
    """get_articles() category_id filter returns only articles in that category."""
    from app.crud.article import get_articles

    cat = _create_category(db_session, "Tech", "tech")
    a1 = _create_article(db_session, "Tech Article", "Body", "Author", ArticleStatus.draft, [cat])
    _create_article(db_session, "No Category", "Body", "Author", ArticleStatus.draft, [])

    articles, total = get_articles(db_session, category_id=cat.id)
    assert total == 1
    assert articles[0].id == a1.id


def test_get_articles_combined_filters(db_session, clean_db):
    """get_articles() handles multiple filters combined."""
    from app.crud.article import get_articles

    cat = _create_category(db_session, "Tech", "tech-combined")
    a1 = _create_article(
        db_session, "Python Guide", "Learn Python", "Alice",
        ArticleStatus.published, [cat]
    )
    _create_article(
        db_session, "Python Draft", "Python info", "Alice",
        ArticleStatus.draft, [cat]
    )
    _create_article(
        db_session, "Other Guide", "Other content", "Bob",
        ArticleStatus.published, [cat]
    )

    articles, total = get_articles(
        db_session,
        search="Python",
        status=ArticleStatus.published,
        author="Alice",
        category_id=cat.id,
    )
    assert total == 1
    assert articles[0].id == a1.id


def test_get_articles_empty_db(db_session, clean_db):
    """get_articles() on empty database returns empty list and zero total."""
    from app.crud.article import get_articles

    articles, total = get_articles(db_session)
    assert articles == []
    assert total == 0


def test_pagination_beyond_last_page(db_session, clean_db):
    """get_articles() beyond last page returns empty list but correct total."""
    from app.crud.article import get_articles

    _create_article(db_session, "Only Article", "Body", "Author", ArticleStatus.draft)

    articles, total = get_articles(db_session, page=999, per_page=10)
    assert total == 1
    assert articles == []
