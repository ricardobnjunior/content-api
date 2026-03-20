"""Tests for category CRUD endpoints and article-category integration."""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Category CRUD tests
# ---------------------------------------------------------------------------


def test_create_category(client: TestClient) -> None:
    """Test that a category can be created and returns correct fields."""
    response = client.post(
        "/api/v1/categories",
        json={"name": "Technology", "description": "Tech articles"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Technology"
    assert data["description"] == "Tech articles"
    assert "id" in data
    assert "slug" in data


def test_create_category_slug_auto_generated(client: TestClient) -> None:
    """Test that slug is automatically generated from the category name."""
    response = client.post(
        "/api/v1/categories",
        json={"name": "My Test Category"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "my-test-category"


def test_create_category_slug_special_chars(client: TestClient) -> None:
    """Test that slug handles special characters correctly."""
    response = client.post(
        "/api/v1/categories",
        json={"name": "Science & Nature"},
    )
    assert response.status_code == 201
    data = response.json()
    # Slug should be lowercase with hyphens, special chars removed/replaced
    assert " " not in data["slug"]
    assert data["slug"] == data["slug"].lower()


def test_create_category_no_description(client: TestClient) -> None:
    """Test that description is optional when creating a category."""
    response = client.post(
        "/api/v1/categories",
        json={"name": "No Description Category"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] is None


def test_create_category_duplicate_name_returns_409(client: TestClient) -> None:
    """Test that creating a category with a duplicate name returns 409."""
    client.post("/api/v1/categories", json={"name": "Duplicate"})
    response = client.post("/api/v1/categories", json={"name": "Duplicate"})
    assert response.status_code == 409


def test_get_categories_empty(client: TestClient) -> None:
    """Test that listing categories returns an empty list when no categories exist."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert response.json() == []


def test_get_categories(client: TestClient) -> None:
    """Test that listing categories returns all created categories."""
    client.post("/api/v1/categories", json={"name": "Cat A"})
    client.post("/api/v1/categories", json={"name": "Cat B"})
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_category_by_id(client: TestClient) -> None:
    """Test retrieving a category by its ID."""
    create_resp = client.post("/api/v1/categories", json={"name": "Findable"})
    category_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Findable"


def test_get_category_not_found(client: TestClient) -> None:
    """Test that requesting a non-existent category returns 404."""
    response = client.get("/api/v1/categories/99999")
    assert response.status_code == 404


def test_update_category(client: TestClient) -> None:
    """Test updating a category's name and description."""
    create_resp = client.post(
        "/api/v1/categories",
        json={"name": "Original Name", "description": "Old desc"},
    )
    category_id = create_resp.json()["id"]

    response = client.put(
        f"/api/v1/categories/{category_id}",
        json={"name": "Updated Name", "description": "New desc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "New desc"
    assert data["slug"] == "updated-name"


def test_update_category_not_found(client: TestClient) -> None:
    """Test that updating a non-existent category returns 404."""
    response = client.put(
        "/api/v1/categories/99999",
        json={"name": "Ghost"},
    )
    assert response.status_code == 404


def test_delete_category(client: TestClient) -> None:
    """Test that a category can be deleted and subsequent GET returns 404."""
    create_resp = client.post("/api/v1/categories", json={"name": "To Delete"})
    category_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/categories/{category_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/v1/categories/{category_id}")
    assert get_resp.status_code == 404


def test_delete_category_not_found(client: TestClient) -> None:
    """Test that deleting a non-existent category returns 404."""
    response = client.delete("/api/v1/categories/99999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Article + category integration tests
# ---------------------------------------------------------------------------


def _create_category(client: TestClient, name: str) -> dict:
    """Helper to create a category and return its JSON data."""
    resp = client.post("/api/v1/categories", json={"name": name})
    assert resp.status_code == 201
    return resp.json()


def _create_article(client: TestClient, category_ids: list[int] | None = None) -> dict:
    """Helper to create an article with optional category IDs."""
    payload: dict = {
        "title": "Test Article",
        "body": "Some body text",
        "author": "Alice",
        "status": "draft",
    }
    if category_ids is not None:
        payload["category_ids"] = category_ids
    resp = client.post("/api/v1/articles", json=payload)
    assert resp.status_code == 201
    return resp.json()


def test_create_article_with_category_ids(client: TestClient) -> None:
    """Test that an article can be created with associated category IDs."""
    cat = _create_category(client, "Python")
    article = _create_article(client, category_ids=[cat["id"]])

    assert "categories" in article
    assert len(article["categories"]) == 1
    assert article["categories"][0]["id"] == cat["id"]
    assert article["categories"][0]["name"] == "Python"


def test_create_article_with_multiple_category_ids(client: TestClient) -> None:
    """Test creating an article with multiple categories."""
    cat1 = _create_category(client, "Backend")
    cat2 = _create_category(client, "Frontend")
    article = _create_article(client, category_ids=[cat1["id"], cat2["id"]])

    assert len(article["categories"]) == 2
    returned_ids = {c["id"] for c in article["categories"]}
    assert cat1["id"] in returned_ids
    assert cat2["id"] in returned_ids


def test_create_article_without_category_ids(client: TestClient) -> None:
    """Test that creating an article without category_ids returns empty categories list."""
    article = _create_article(client, category_ids=None)
    assert "categories" in article
    assert article["categories"] == []


def test_create_article_with_nonexistent_category_ids(client: TestClient) -> None:
    """Test that nonexistent category IDs are silently ignored."""
    article = _create_article(client, category_ids=[99999, 88888])
    assert "categories" in article
    assert article["categories"] == []


def test_get_article_includes_categories(client: TestClient) -> None:
    """Test that GET /articles/{id} response includes the categories field."""
    cat = _create_category(client, "DevOps")
    article = _create_article(client, category_ids=[cat["id"]])
    article_id = article["id"]

    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) == 1
    assert data["categories"][0]["name"] == "DevOps"


def test_update_article_clears_categories(client: TestClient) -> None:
    """Test that updating an article with empty category_ids clears its categories."""
    cat = _create_category(client, "Infrastructure")
    article = _create_article(client, category_ids=[cat["id"]])
    article_id = article["id"]

    # Update with empty category_ids should clear categories
    update_resp = client.put(
        f"/api/v1/articles/{article_id}",
        json={"title": "Updated Title", "category_ids": []},
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["categories"] == []


def test_update_article_changes_categories(client: TestClient) -> None:
    """Test that updating an article with new category_ids replaces categories."""
    cat1 = _create_category(client, "Old Category")
    cat2 = _create_category(client, "New Category")
    article = _create_article(client, category_ids=[cat1["id"]])
    article_id = article["id"]

    update_resp = client.put(
        f"/api/v1/articles/{article_id}",
        json={"title": "Updated", "category_ids": [cat2["id"]]},
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert len(data["categories"]) == 1
    assert data["categories"][0]["id"] == cat2["id"]


def test_delete_category_does_not_delete_article(client: TestClient) -> None:
    """Test that deleting a category does not delete associated articles."""
    cat = _create_category(client, "Temporary")
    article = _create_article(client, category_ids=[cat["id"]])
    article_id = article["id"]

    client.delete(f"/api/v1/categories/{cat['id']}")

    article_resp = client.get(f"/api/v1/articles/{article_id}")
    assert article_resp.status_code == 200
    # Categories list should be empty now
    assert article_resp.json()["categories"] == []
