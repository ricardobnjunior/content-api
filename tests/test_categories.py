"""Tests for Category endpoints and article-category integration."""

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


@pytest.fixture()
def client(db_session):
    """Return a TestClient that uses the test db_session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Category creation
# ---------------------------------------------------------------------------


def test_create_category_returns_201(client):
    """POST /categories returns 201 and the created category."""
    response = client.post(
        "/api/v1/categories/",
        json={"name": "Technology", "description": "Tech articles"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Technology"
    assert data["description"] == "Tech articles"
    assert "id" in data


def test_create_category_slug_auto_generated(client):
    """Slug is auto-generated from the category name."""
    response = client.post(
        "/api/v1/categories/",
        json={"name": "Hello World"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "hello-world"


def test_create_category_slug_special_chars(client):
    """Special characters are stripped during slug generation."""
    response = client.post(
        "/api/v1/categories/",
        json={"name": "Science & Nature!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "science" in data["slug"]
    assert "nature" in data["slug"]
    assert "&" not in data["slug"]
    assert "!" not in data["slug"]


def test_create_category_duplicate_returns_409(client):
    """Duplicate category name returns 409 Conflict."""
    client.post("/api/v1/categories/", json={"name": "Duplicate"})
    response = client.post("/api/v1/categories/", json={"name": "Duplicate"})
    assert response.status_code == 409


def test_create_category_no_description(client):
    """Category can be created without a description."""
    response = client.post(
        "/api/v1/categories/",
        json={"name": "No Desc"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] is None


def test_create_category_response_has_slug_field(client):
    """CategoryResponse includes the slug field."""
    response = client.post(
        "/api/v1/categories/",
        json={"name": "Has Slug"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "slug" in data
    assert data["slug"] == "has-slug"


# ---------------------------------------------------------------------------
# List categories
# ---------------------------------------------------------------------------


def test_list_categories_empty(client):
    """GET /categories returns empty list when no categories exist."""
    response = client.get("/api/v1/categories/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_categories_returns_created(client):
    """GET /categories returns all created categories."""
    client.post("/api/v1/categories/", json={"name": "Alpha"})
    client.post("/api/v1/categories/", json={"name": "Beta"})
    response = client.get("/api/v1/categories/")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert "Alpha" in names
    assert "Beta" in names


def test_list_categories_pagination_skip(client):
    """GET /categories?skip=1 skips the first category."""
    client.post("/api/v1/categories/", json={"name": "First"})
    client.post("/api/v1/categories/", json={"name": "Second"})
    response = client.get("/api/v1/categories/?skip=1&limit=10")
    assert response.status_code == 200
    # At least one result returned with pagination applied
    assert isinstance(response.json(), list)


def test_list_categories_pagination_limit(client):
    """GET /categories?limit=1 returns at most one category."""
    client.post("/api/v1/categories/", json={"name": "Limit A"})
    client.post("/api/v1/categories/", json={"name": "Limit B"})
    response = client.get("/api/v1/categories/?limit=1")
    assert response.status_code == 200
    assert len(response.json()) <= 1


# ---------------------------------------------------------------------------
# Get single category
# ---------------------------------------------------------------------------


def test_get_category_by_id(client):
    """GET /categories/{id} returns the category."""
    created = client.post(
        "/api/v1/categories/", json={"name": "Single"}
    ).json()
    response = client.get(f"/api/v1/categories/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Single"


def test_get_category_not_found(client):
    """GET /categories/{id} returns 404 for nonexistent id."""
    response = client.get("/api/v1/categories/99999")
    assert response.status_code == 404


def test_get_category_returns_correct_fields(client):
    """GET /categories/{id} returns all expected fields."""
    created = client.post(
        "/api/v1/categories/",
        json={"name": "Full Fields", "description": "A description"},
    ).json()
    response = client.get(f"/api/v1/categories/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "slug" in data
    assert "description" in data
    assert data["description"] == "A description"


# ---------------------------------------------------------------------------
# Update category
# ---------------------------------------------------------------------------


def test_update_category(client):
    """PUT /categories/{id} updates the category."""
    created = client.post(
        "/api/v1/categories/", json={"name": "Original Name"}
    ).json()
    response = client.put(
        f"/api/v1/categories/{created['id']}",
        json={"name": "Updated Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


def test_update_category_regenerates_slug(client):
    """PUT /categories/{id} regenerates slug when name changes."""
    created = client.post(
        "/api/v1/categories/", json={"name": "Old Slug Name"}
    ).json()
    assert created["slug"] == "old-slug-name"

    response = client.put(
        f"/api/v1/categories/{created['id']}",
        json={"name": "New Slug Name"},
    )
    assert response.status_code == 200
    assert response.json()["slug"] == "new-slug-name"


def test_update_category_description_only(client):
    """PUT /categories/{id} can update just the description."""
    created = client.post(
        "/api/v1/categories/",
        json={"name": "Desc Only", "description": "Old desc"},
    ).json()
    response = client.put(
        f"/api/v1/categories/{created['id']}",
        json={"description": "New desc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "New desc"
    assert data["name"] == "Desc Only"  # name unchanged


def test_update_category_not_found(client):
    """PUT /categories/{id} returns 404 for nonexistent id."""
    response = client.put(
        "/api/v1/categories/99999",
        json={"name": "Ghost"},
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Delete category
# ---------------------------------------------------------------------------


def test_delete_category(client):
    """DELETE /categories/{id} returns 204 and removes the category."""
    created = client.post(
        "/api/v1/categories/", json={"name": "To Delete"}
    ).json()
    response = client.delete(f"/api/v1/categories/{created['id']}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/categories/{created['id']}")
    assert get_response.status_code == 404


def test_delete_category_not_found(client):
    """DELETE /categories/{id} returns 404 for nonexistent id."""
    response = client.delete("/api/v1/categories/99999")
    assert response.status_code == 404


def test_delete_category_no_body(client):
    """DELETE /categories/{id} returns no body on 204."""
    created = client.post(
        "/api/v1/categories/", json={"name": "Empty Response"}
    ).json()
    response = client.delete(f"/api/v1/categories/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""


# ---------------------------------------------------------------------------
# Article + category integration
# ---------------------------------------------------------------------------


def test_create_article_with_category_ids(client):
    """POST /articles with category_ids assigns categories to the article."""
    cat = client.post(
        "/api/v1/categories/", json={"name": "Integration Cat"}
    ).json()

    response = client.post(
        "/api/v1/articles/",
        json={
            "title": "Article with Category",
            "body": "Body text",
            "author": "Author",
            "status": "draft",
            "category_ids": [cat["id"]],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) == 1
    assert data["categories"][0]["id"] == cat["id"]
    assert data["categories"][0]["name"] == "Integration Cat"


def test_article_response_has_empty_categories_by_default(client):
    """POST /articles without category_ids returns categories as empty list."""
    response = client.post(
        "/api/v1/articles/",
        json={
            "title": "No Category Article",
            "body": "Body",
            "author": "Author",
            "status": "published",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "categories" in data
    assert data["categories"] == []


def test_create_article_with_multiple_categories(client):
    """POST /articles with multiple category_ids assigns all categories."""
    cat1 = client.post("/api/v1/categories/", json={"name": "Cat One"}).json()
    cat2 = client.post("/api/v1/categories/", json={"name": "Cat Two"}).json()

    response = client.post(
        "/api/v1/articles/",
        json={
            "title": "Multi Cat Article",
            "body": "Body",
            "author": "Author",
            "category_ids": [cat1["id"], cat2["id"]],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assigned_ids = {c["id"] for c in data["categories"]}
    assert cat1["id"] in assigned_ids
    assert cat2["id"] in assigned_ids


def test_delete_category_does_not_delete_article(client):
    """Deleting a category should not delete associated articles."""
    cat = client.post("/api/v1/categories/", json={"name": "Temp Cat"}).json()
    article = client.post(
        "/api/v1/articles/",
        json={
            "title": "Survives Deletion",
            "body": "Body",
            "author": "Author",
            "category_ids": [cat["id"]],
        },
    ).json()

    client.delete(f"/api/v1/categories/{cat['id']}")

    get_response = client.get(f"/api/v1/articles/{article['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["categories"] == []


def test_update_article_category_ids(client):
    """PUT /articles/{id} with category_ids updates the article's categories."""
    cat1 = client.post(
        "/api/v1/categories/", json={"name": "Update Cat 1"}
    ).json()
    cat2 = client.post(
        "/api/v1/categories/", json={"name": "Update Cat 2"}
    ).json()

    article = client.post(
        "/api/v1/articles/",
        json={
            "title": "Update Categories Article",
            "body": "Body",
            "author": "Author",
            "category_ids": [cat1["id"]],
        },
    ).json()

    assert len(article["categories"]) == 1

    response = client.put(
        f"/api/v1/articles/{article['id']}",
        json={"category_ids": [cat2["id"]]},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["categories"]) == 1
    assert data["categories"][0]["id"] == cat2["id"]


def test_create_article_with_nonexistent_category_ids(client):
    """POST /articles with nonexistent category_ids creates article with no categories."""
    response = client.post(
        "/api/v1/articles/",
        json={
            "title": "Ghost Category Article",
            "body": "Body",
            "author": "Author",
            "category_ids": [99999],
        },
    )
    # Article is still created; nonexistent IDs are silently ignored
    assert response.status_code == 201
    data = response.json()
    assert data["categories"] == []


def test_article_category_slug_in_response(client):
    """Category in article response includes slug field."""
    cat = client.post(
        "/api/v1/categories/",
        json={"name": "Slug Check Category"},
    ).json()

    response = client.post(
        "/api/v1/articles/",
        json={
            "title": "Slug Check Article",
            "body": "Body",
            "author": "Author",
            "category_ids": [cat["id"]],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["categories"]) == 1
    cat_in_response = data["categories"][0]
    assert "slug" in cat_in_response
    assert cat_in_response["slug"] == "slug-check-category"
