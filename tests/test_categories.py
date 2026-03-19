"""Tests for Category endpoints and article-category relationships."""

import pytest
from fastapi.testclient import TestClient



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_category(client: TestClient, name: str, description: str | None = None) -> dict:
    """Helper to create a category and assert success."""
    payload: dict = {"name": name}
    if description is not None:
        payload["description"] = description
    response = client.post("/api/v1/categories", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_article(client: TestClient, **kwargs) -> dict:
    """Helper to create an article and assert success."""
    payload = {
        "title": kwargs.get("title", "Test Article"),
        "body": kwargs.get("body", "Body content"),
        "author": kwargs.get("author", "Author"),
        "status": kwargs.get("status", "draft"),
        "category_ids": kwargs.get("category_ids", []),
    }
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# Category CRUD Tests
# ---------------------------------------------------------------------------

class TestCreateCategory:
    """Tests for POST /api/v1/categories."""

    def test_create_category_returns_201(self, client: TestClient) -> None:
        """Creating a category returns 201 with correct fields."""
        data = _create_category(client, "Technology", "Tech articles")
        assert data["name"] == "Technology"
        assert data["slug"] == "technology"
        assert data["description"] == "Tech articles"
        assert "id" in data

    def test_slug_auto_generated_from_name(self, client: TestClient) -> None:
        """Slug is auto-generated as lowercase hyphenated form of name."""
        data = _create_category(client, "Hello World")
        assert data["slug"] == "hello-world"

    def test_slug_strips_special_characters(self, client: TestClient) -> None:
        """Slug normalizes special characters correctly."""
        data = _create_category(client, "Tech & Science!")
        assert data["slug"] == "tech-science"

    def test_slug_from_unicode_name(self, client: TestClient) -> None:
        """Slug is generated correctly from names with accented characters."""
        data = _create_category(client, "Caf\u00e9 Culture")
        assert data["slug"] == "cafe-culture"

    def test_duplicate_name_returns_409(self, client: TestClient) -> None:
        """Creating a category with a duplicate name returns 409."""
        _create_category(client, "Duplicate")
        response = client.post("/api/v1/categories", json={"name": "Duplicate"})
        assert response.status_code == 409

    def test_create_category_without_description(self, client: TestClient) -> None:
        """Creating a category without description sets description to None."""
        data = _create_category(client, "No Description")
        assert data["description"] is None


class TestGetCategory:
    """Tests for GET /api/v1/categories/{category_id}."""

    def test_get_existing_category(self, client: TestClient) -> None:
        """Fetching an existing category returns 200 with correct data."""
        created = _create_category(client, "Existing Category")
        response = client.get(f"/api/v1/categories/{created['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created["id"]
        assert data["name"] == "Existing Category"

    def test_get_nonexistent_category_returns_404(self, client: TestClient) -> None:
        """Fetching a nonexistent category returns 404."""
        response = client.get("/api/v1/categories/99999")
        assert response.status_code == 404


class TestListCategories:
    """Tests for GET /api/v1/categories."""

    def test_list_categories_returns_200(self, client: TestClient) -> None:
        """Listing categories returns 200 with a list."""
        _create_category(client, "ListCat1")
        _create_category(client, "ListCat2")
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        names = [c["name"] for c in data]
        assert "ListCat1" in names
        assert "ListCat2" in names

    def test_list_categories_skip_limit(self, client: TestClient) -> None:
        """Listing categories respects skip and limit query params."""
        for i in range(5):
            _create_category(client, f"SkipCat{i}")
        response = client.get("/api/v1/categories?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_list_empty_returns_empty_list(self, client: TestClient) -> None:
        """Listing when no categories exist returns empty list."""
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        assert response.json() == []


class TestUpdateCategory:
    """Tests for PUT /api/v1/categories/{category_id}."""

    def test_update_category_name_and_slug(self, client: TestClient) -> None:
        """Updating a category's name also updates the slug."""
        created = _create_category(client, "Old Name")
        response = client.put(
            f"/api/v1/categories/{created['id']}",
            json={"name": "New Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["slug"] == "new-name"

    def test_update_category_description(self, client: TestClient) -> None:
        """Updating a category's description works correctly."""
        created = _create_category(client, "Update Desc Cat")
        response = client.put(
            f"/api/v1/categories/{created['id']}",
            json={"description": "Updated description"},
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"

    def test_update_nonexistent_category_returns_404(self, client: TestClient) -> None:
        """Updating a nonexistent category returns 404."""
        response = client.put("/api/v1/categories/99999", json={"name": "X"})
        assert response.status_code == 404


class TestDeleteCategory:
    """Tests for DELETE /api/v1/categories/{category_id}."""

    def test_delete_existing_category_returns_204(self, client: TestClient) -> None:
        """Deleting an existing category returns 204."""
        created = _create_category(client, "To Delete")
        response = client.delete(f"/api/v1/categories/{created['id']}")
        assert response.status_code == 204

    def test_deleted_category_not_found(self, client: TestClient) -> None:
        """After deletion, GET on the category returns 404."""
        created = _create_category(client, "Gone Category")
        client.delete(f"/api/v1/categories/{created['id']}")
        response = client.get(f"/api/v1/categories/{created['id']}")
        assert response.status_code == 404

    def test_delete_nonexistent_category_returns_404(self, client: TestClient) -> None:
        """Deleting a nonexistent category returns 404."""
        response = client.delete("/api/v1/categories/99999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Article-Category Relationship Tests
# ---------------------------------------------------------------------------

class TestArticleWithCategories:
    """Tests for article creation and update with category_ids."""

    def test_create_article_without_category_ids(self, client: TestClient) -> None:
        """Article created without category_ids has empty categories list."""
        data = _create_article(client, title="No Categories")
        assert data["categories"] == []

    def test_create_article_with_single_category(self, client: TestClient) -> None:
        """Article created with one category_id includes the category in response."""
        cat = _create_category(client, "Single Cat")
        data = _create_article(client, title="One Cat Article", category_ids=[cat["id"]])
        assert len(data["categories"]) == 1
        assert data["categories"][0]["id"] == cat["id"]
        assert data["categories"][0]["name"] == "Single Cat"

    def test_create_article_with_multiple_categories(self, client: TestClient) -> None:
        """Article created with multiple category_ids includes all categories."""
        cat1 = _create_category(client, "Multi Cat A")
        cat2 = _create_category(client, "Multi Cat B")
        data = _create_article(
            client,
            title="Multi Cat Article",
            category_ids=[cat1["id"], cat2["id"]],
        )
        assert len(data["categories"]) == 2
        returned_ids = {c["id"] for c in data["categories"]}
        assert cat1["id"] in returned_ids
        assert cat2["id"] in returned_ids

    def test_update_article_replaces_categories(self, client: TestClient) -> None:
        """Updating an article with new category_ids replaces the existing ones."""
        cat1 = _create_category(client, "Replace Cat A")
        cat2 = _create_category(client, "Replace Cat B")
        article = _create_article(client, title="Replace Cats", category_ids=[cat1["id"]])

        response = client.put(
            f"/api/v1/articles/{article['id']}",
            json={"category_ids": [cat2["id"]]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["categories"]) == 1
        assert data["categories"][0]["id"] == cat2["id"]

    def test_update_article_clears_categories(self, client: TestClient) -> None:
        """Updating an article with empty category_ids clears all categories."""
        cat = _create_category(client, "Clear Cat")
        article = _create_article(client, title="Clear Cats", category_ids=[cat["id"]])

        response = client.put(
            f"/api/v1/articles/{article['id']}",
            json={"category_ids": []},
        )
        assert response.status_code == 200
        assert response.json()["categories"] == []

    def test_delete_category_does_not_delete_article(self, client: TestClient) -> None:
        """Deleting a category does not delete associated articles."""
        cat = _create_category(client, "Cascade Cat")
        article = _create_article(client, title="Cascade Article", category_ids=[cat["id"]])

        client.delete(f"/api/v1/categories/{cat['id']}")

        response = client.get(f"/api/v1/articles/{article['id']}")
        assert response.status_code == 200
        assert response.json()["categories"] == []

    def test_create_article_with_invalid_category_id(self, client: TestClient) -> None:
        """Article created with nonexistent category_ids ignores them gracefully."""
        data = _create_article(client, title="Invalid Cat Article", category_ids=[99999])
        assert data["categories"] == []
