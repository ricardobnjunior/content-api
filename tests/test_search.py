"""Tests for article search, filtering, and pagination endpoints."""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_article(
    client: TestClient,
    title: str = "Test Article",
    body: str = "Test body content",
    status: str = "draft",
    author: str = "Alice",
    category_ids: list[int] | None = None,
) -> dict:
    """POST a new article and return the response JSON."""
    payload = {
        "title": title,
        "body": body,
        "status": status,
        "author": author,
        "category_ids": category_ids or [],
    }
    response = client.post("/api/v1/articles/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_category(client: TestClient, name: str = "Tech") -> dict:
    """POST a new category and return the response JSON."""
    response = client.post("/api/v1/categories/", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_search_by_title_substring(client: TestClient) -> None:
    """Search by a unique partial title should return only the matching article."""
    _create_article(client, title="Python Tutorial Introduction", body="All about python")
    _create_article(client, title="JavaScript Guide", body="All about js")

    response = client.get("/api/v1/articles/", params={"search": "Tutorial Introduction"})
    assert response.status_code == 200
    data = response.json()

    assert data["meta"]["total"] == 1
    assert len(data["items"]) == 1
    assert "Tutorial Introduction" in data["items"][0]["title"]


def test_search_by_body_substring(client: TestClient) -> None:
    """Search by a unique partial body should return only the matching article."""
    _create_article(client, title="Article A", body="unique_body_phrase_xyz content here")
    _create_article(client, title="Article B", body="completely different content")

    response = client.get("/api/v1/articles/", params={"search": "unique_body_phrase_xyz"})
    assert response.status_code == 200
    data = response.json()

    assert data["meta"]["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Article A"


def test_filter_by_status_draft(client: TestClient) -> None:
    """Filtering by status=draft should return only draft articles."""
    _create_article(client, title="Draft One", status="draft")
    _create_article(client, title="Published One", status="published")

    response = client.get("/api/v1/articles/", params={"status": "draft"})
    assert response.status_code == 200
    data = response.json()

    for item in data["items"]:
        assert item["status"] == "draft"
    titles = [item["title"] for item in data["items"]]
    assert "Draft One" in titles
    assert "Published One" not in titles


def test_filter_by_status_published(client: TestClient) -> None:
    """Filtering by status=published should return only published articles."""
    _create_article(client, title="Draft Two", status="draft")
    _create_article(client, title="Published Two", status="published")

    response = client.get("/api/v1/articles/", params={"status": "published"})
    assert response.status_code == 200
    data = response.json()

    for item in data["items"]:
        assert item["status"] == "published"
    titles = [item["title"] for item in data["items"]]
    assert "Published Two" in titles
    assert "Draft Two" not in titles


def test_filter_by_author(client: TestClient) -> None:
    """Filtering by author should return only articles by that author."""
    _create_article(client, title="By Alice", author="Alice")
    _create_article(client, title="By Bob", author="Bob")
    _create_article(client, title="Also By Alice", author="Alice")

    response = client.get("/api/v1/articles/", params={"author": "Alice"})
    assert response.status_code == 200
    data = response.json()

    assert data["meta"]["total"] == 2
    for item in data["items"]:
        assert item["author"] == "Alice"


def test_filter_by_category_id(client: TestClient) -> None:
    """Filtering by category_id should return only articles in that category."""
    category = _create_category(client, name="Science")
    category_id = category["id"]

    _create_article(client, title="Science Article", category_ids=[category_id])
    _create_article(client, title="No Category Article", category_ids=[])

    response = client.get("/api/v1/articles/", params={"category_id": category_id})
    assert response.status_code == 200
    data = response.json()

    assert data["meta"]["total"] == 1
    assert data["items"][0]["title"] == "Science Article"


def test_pagination_page1_vs_page2(client: TestClient) -> None:
    """Page 1 and page 2 should contain different, non-overlapping articles."""
    for i in range(3):
        _create_article(client, title=f"Paginated Article {i}", author="PaginationAuthor")

    resp1 = client.get(
        "/api/v1/articles/",
        params={"author": "PaginationAuthor", "per_page": 2, "page": 1},
    )
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert len(data1["items"]) == 2
    assert data1["meta"]["total"] == 3
    assert data1["meta"]["pages"] == 2
    assert data1["meta"]["page"] == 1
    assert data1["meta"]["per_page"] == 2

    resp2 = client.get(
        "/api/v1/articles/",
        params={"author": "PaginationAuthor", "per_page": 2, "page": 2},
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2["items"]) == 1
    assert data2["meta"]["page"] == 2

    ids1 = {item["id"] for item in data1["items"]}
    ids2 = {item["id"] for item in data2["items"]}
    assert ids1.isdisjoint(ids2), "Page 1 and page 2 must not share any article IDs"


def test_combined_search_and_status(client: TestClient) -> None:
    """Combined search + status filter should match both conditions simultaneously."""
    _create_article(
        client,
        title="Combo Match Article",
        body="special_combo_term content",
        status="published",
        author="Combo Author",
    )
    _create_article(
        client,
        title="Combo No Match Article",
        body="special_combo_term content",
        status="draft",
        author="Combo Author",
    )
    _create_article(
        client,
        title="Unrelated Published",
        body="no search term",
        status="published",
        author="Combo Author",
    )

    response = client.get(
        "/api/v1/articles/",
        params={"search": "special_combo_term", "status": "published"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["meta"]["total"] == 1
    assert data["items"][0]["title"] == "Combo Match Article"
    assert data["items"][0]["status"] == "published"


def test_empty_results(client: TestClient) -> None:
    """Search with no matches should return empty items list with correct meta."""
    response = client.get(
        "/api/v1/articles/",
        params={"search": "nonexistentxyz_impossibleterm_12345"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["items"] == []
    assert data["meta"]["total"] == 0
    assert data["meta"]["pages"] == 0


def test_meta_fields_present(client: TestClient) -> None:
    """Response must always include a meta object with the required pagination fields."""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()

    assert "meta" in data
    meta = data["meta"]
    assert "total" in meta
    assert "page" in meta
    assert "per_page" in meta
    assert "pages" in meta

    assert isinstance(meta["total"], int)
    assert isinstance(meta["page"], int)
    assert isinstance(meta["per_page"], int)
    assert isinstance(meta["pages"], int)


def test_search_case_insensitive(client: TestClient) -> None:
    """Search should be case-insensitive for both title and body matching."""
    _create_article(
        client,
        title="CamelCase Title Article",
        body="Normal body",
        author="CaseAuthor",
    )

    response = client.get(
        "/api/v1/articles/",
        params={"search": "camelcase title", "author": "CaseAuthor"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["meta"]["total"] == 1
    assert data["items"][0]["title"] == "CamelCase Title Article"


def test_pagination_default_values(client: TestClient) -> None:
    """Default page=1 and per_page=20 should be reflected in meta."""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()

    assert data["meta"]["page"] == 1
    assert data["meta"]["per_page"] == 20


def test_per_page_validation_too_large(client: TestClient) -> None:
    """per_page > 100 should return 422 validation error."""
    response = client.get("/api/v1/articles/", params={"per_page": 101})
    assert response.status_code == 422


def test_page_validation_zero(client: TestClient) -> None:
    """page=0 should return 422 validation error (ge=1 constraint)."""
    response = client.get("/api/v1/articles/", params={"page": 0})
    assert response.status_code == 422


def test_filter_by_multiple_categories(client: TestClient) -> None:
    """Articles in one category should not appear when filtering by a different category."""
    cat_a = _create_category(client, name="CategoryA")
    cat_b = _create_category(client, name="CategoryB")

    _create_article(client, title="In Category A", category_ids=[cat_a["id"]])
    _create_article(client, title="In Category B", category_ids=[cat_b["id"]])

    response = client.get("/api/v1/articles/", params={"category_id": cat_a["id"]})
    assert response.status_code == 200
    data = response.json()

    assert data["meta"]["total"] == 1
    assert data["items"][0]["title"] == "In Category A"


def test_invalid_status_filter(client: TestClient) -> None:
    """An invalid status value should return 422 validation error."""
    response = client.get("/api/v1/articles/", params={"status": "invalid_status"})
    assert response.status_code == 422
