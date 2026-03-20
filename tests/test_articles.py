"""Tests for Article CRUD REST endpoints."""

import pytest
from starlette.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def article_payload() -> dict:
    """Return a valid article creation payload."""
    return {
        "title": "Test Article",
        "body": "This is the body of the test article.",
        "author": "Jane Doe",
    }


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


def test_create_article(client: TestClient, article_payload: dict) -> None:
    """POST /api/v1/articles creates an article and returns 201."""
    response = client.post("/api/v1/articles/", json=article_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == article_payload["title"]
    assert data["body"] == article_payload["body"]
    assert data["author"] == article_payload["author"]
    assert data["status"] == "draft"
    assert "id" in data
    assert data["id"] > 0


def test_create_article_published(client: TestClient, article_payload: dict) -> None:
    """POST with status='published' creates a published article."""
    payload = {**article_payload, "status": "published"}
    response = client.post("/api/v1/articles/", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "published"


def test_create_article_validation_empty_title(
    client: TestClient, article_payload: dict
) -> None:
    """POST with empty title returns 422 validation error."""
    payload = {**article_payload, "title": ""}
    response = client.post("/api/v1/articles/", json=payload)
    assert response.status_code == 422


def test_create_article_validation_missing_body(client: TestClient) -> None:
    """POST without body field returns 422 validation error."""
    payload = {"title": "No Body Article", "author": "Author"}
    response = client.post("/api/v1/articles/", json=payload)
    assert response.status_code == 422


def test_create_article_title_too_long(client: TestClient, article_payload: dict) -> None:
    """POST with title exceeding 200 chars returns 422."""
    payload = {**article_payload, "title": "x" * 201}
    response = client.post("/api/v1/articles/", json=payload)
    assert response.status_code == 422


def test_create_article_author_too_long(client: TestClient, article_payload: dict) -> None:
    """POST with author exceeding 100 chars returns 422."""
    payload = {**article_payload, "author": "a" * 101}
    response = client.post("/api/v1/articles/", json=payload)
    assert response.status_code == 422


def test_create_article_invalid_status(client: TestClient, article_payload: dict) -> None:
    """POST with invalid status value returns 422."""
    payload = {**article_payload, "status": "archived"}
    response = client.post("/api/v1/articles/", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Read single
# ---------------------------------------------------------------------------


def test_get_article(client: TestClient, article_payload: dict) -> None:
    """GET /api/v1/articles/{id} returns the created article."""
    create_response = client.post("/api/v1/articles/", json=article_payload)
    assert create_response.status_code == 201
    article_id = create_response.json()["id"]

    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == article_payload["title"]


def test_get_article_not_found(client: TestClient) -> None:
    """GET /api/v1/articles/99999 returns 404."""
    response = client.get("/api/v1/articles/99999")
    assert response.status_code == 404


def test_get_article_response_fields(client: TestClient, article_payload: dict) -> None:
    """GET returns article with all expected fields."""
    create_resp = client.post("/api/v1/articles/", json=article_payload)
    article_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/articles/{article_id}")
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "body" in data
    assert "author" in data
    assert "status" in data
    assert "created_at" in data
    assert "updated_at" in data


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


def test_list_articles_empty(client: TestClient) -> None:
    """GET /api/v1/articles on an empty database returns empty list."""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_articles(client: TestClient, article_payload: dict) -> None:
    """GET /api/v1/articles after creating articles returns correct total."""
    for i in range(3):
        payload = {**article_payload, "title": f"Article {i}"}
        resp = client.post("/api/v1/articles/", json=payload)
        assert resp.status_code == 201

    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_list_articles_pagination(client: TestClient, article_payload: dict) -> None:
    """GET /api/v1/articles with skip/limit returns correct page."""
    for i in range(5):
        payload = {**article_payload, "title": f"Article {i}"}
        resp = client.post("/api/v1/articles/", json=payload)
        assert resp.status_code == 201

    response = client.get("/api/v1/articles/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


def test_list_articles_skip_all(client: TestClient, article_payload: dict) -> None:
    """GET with skip >= total returns empty items but correct total."""
    for i in range(2):
        payload = {**article_payload, "title": f"Article {i}"}
        client.post("/api/v1/articles/", json=payload)

    response = client.get("/api/v1/articles/?skip=10&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["items"] == []


def test_list_articles_default_limit(client: TestClient, article_payload: dict) -> None:
    """GET without params uses default skip=0, limit=20."""
    for i in range(3):
        payload = {**article_payload, "title": f"Article {i}"}
        client.post("/api/v1/articles/", json=payload)

    response = client.get("/api/v1/articles/")
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


def test_update_article(client: TestClient, article_payload: dict) -> None:
    """PUT /api/v1/articles/{id} updates and returns the article."""
    create_resp = client.post("/api/v1/articles/", json=article_payload)
    assert create_resp.status_code == 201
    article_id = create_resp.json()["id"]

    update_payload = {"title": "Updated Title", "body": "Updated body content."}
    response = client.put(f"/api/v1/articles/{article_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["body"] == "Updated body content."
    assert data["author"] == article_payload["author"]


def test_update_article_partial(client: TestClient, article_payload: dict) -> None:
    """PUT with only status field leaves other fields unchanged."""
    create_resp = client.post("/api/v1/articles/", json=article_payload)
    assert create_resp.status_code == 201
    article_id = create_resp.json()["id"]
    original_title = create_resp.json()["title"]

    response = client.put(
        f"/api/v1/articles/{article_id}", json={"status": "published"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert data["title"] == original_title


def test_update_article_not_found(client: TestClient) -> None:
    """PUT /api/v1/articles/99999 returns 404."""
    response = client.put("/api/v1/articles/99999", json={"title": "Ghost"})
    assert response.status_code == 404


def test_update_article_empty_body_is_valid(
    client: TestClient, article_payload: dict
) -> None:
    """PUT with empty payload (no fields) leaves article unchanged."""
    create_resp = client.post("/api/v1/articles/", json=article_payload)
    article_id = create_resp.json()["id"]
    original_title = create_resp.json()["title"]

    response = client.put(f"/api/v1/articles/{article_id}", json={})
    assert response.status_code == 200
    assert response.json()["title"] == original_title


def test_update_article_invalid_status(
    client: TestClient, article_payload: dict
) -> None:
    """PUT with invalid status value returns 422."""
    create_resp = client.post("/api/v1/articles/", json=article_payload)
    article_id = create_resp.json()["id"]

    response = client.put(f"/api/v1/articles/{article_id}", json={"status": "deleted"})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


def test_delete_article(client: TestClient, article_payload: dict) -> None:
    """DELETE /api/v1/articles/{id} returns 204; subsequent GET returns 404."""
    create_resp = client.post("/api/v1/articles/", json=article_payload)
    assert create_resp.status_code == 201
    article_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/articles/{article_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/v1/articles/{article_id}")
    assert get_resp.status_code == 404


def test_delete_article_not_found(client: TestClient) -> None:
    """DELETE /api/v1/articles/99999 returns 404."""
    response = client.delete("/api/v1/articles/99999")
    assert response.status_code == 404


def test_delete_article_removes_from_list(
    client: TestClient, article_payload: dict
) -> None:
    """After deleting, total count decreases."""
    create_resp = client.post("/api/v1/articles/", json=article_payload)
    article_id = create_resp.json()["id"]

    before = client.get("/api/v1/articles/").json()
    assert before["total"] == 1

    client.delete(f"/api/v1/articles/{article_id}")

    after = client.get("/api/v1/articles/").json()
    assert after["total"] == 0
    assert after["items"] == []


# ---------------------------------------------------------------------------
# Default status
# ---------------------------------------------------------------------------


def test_default_status_is_draft(client: TestClient, article_payload: dict) -> None:
    """Article created without explicit status defaults to 'draft'."""
    payload = {k: v for k, v in article_payload.items() if k != "status"}
    response = client.post("/api/v1/articles/", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "draft"
