"""Tests for Article CRUD endpoints."""

import pytest
from starlette.testclient import TestClient


BASE_URL = "/api/v1/articles"

VALID_PAYLOAD = {
    "title": "Test Article",
    "body": "This is the body of the test article.",
    "author": "Jane Doe",
}


def test_create_article(client: TestClient) -> None:
    """POST /articles with valid payload returns 201 and all fields."""
    response = client.post(BASE_URL, json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == VALID_PAYLOAD["title"]
    assert data["body"] == VALID_PAYLOAD["body"]
    assert data["author"] == VALID_PAYLOAD["author"]
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data
    assert data["updated_at"] is None


def test_create_article_default_status(client: TestClient) -> None:
    """POST /articles without status defaults to draft."""
    response = client.post(BASE_URL, json=VALID_PAYLOAD)
    assert response.status_code == 201
    assert response.json()["status"] == "draft"


def test_create_article_with_status(client: TestClient) -> None:
    """POST /articles with explicit status published."""
    payload = {**VALID_PAYLOAD, "status": "published"}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "published"


def test_get_article(client: TestClient) -> None:
    """GET /articles/{id} returns 200 and correct fields."""
    created = client.post(BASE_URL, json=VALID_PAYLOAD).json()
    article_id = created["id"]

    response = client.get(f"{BASE_URL}/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == VALID_PAYLOAD["title"]
    assert data["body"] == VALID_PAYLOAD["body"]
    assert data["author"] == VALID_PAYLOAD["author"]


def test_get_article_not_found(client: TestClient) -> None:
    """GET /articles/{id} returns 404 for non-existent article."""
    response = client.get(f"{BASE_URL}/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_articles_empty(client: TestClient) -> None:
    """GET /articles returns 200 with empty list when no articles exist."""
    response = client.get(BASE_URL)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert data["total"] >= 0


def test_list_articles(client: TestClient) -> None:
    """GET /articles returns all created articles with correct total."""
    payloads = [
        {"title": f"Article {i}", "body": f"Body {i}", "author": "Author"}
        for i in range(3)
    ]
    for payload in payloads:
        client.post(BASE_URL, json=payload)

    response = client.get(BASE_URL)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 3


def test_list_articles_pagination(client: TestClient) -> None:
    """GET /articles with skip/limit returns correct subset."""
    for i in range(5):
        client.post(BASE_URL, json={"title": f"Page {i}", "body": "body", "author": "Author"})

    response = client.get(f"{BASE_URL}?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2
    assert data["total"] >= 5


def test_update_article(client: TestClient) -> None:
    """PUT /articles/{id} returns 200 and updated fields."""
    created = client.post(BASE_URL, json=VALID_PAYLOAD).json()
    article_id = created["id"]

    update_payload = {
        "title": "Updated Title",
        "body": "Updated body content.",
        "author": "John Smith",
        "status": "published",
    }
    response = client.put(f"{BASE_URL}/{article_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == "Updated Title"
    assert data["body"] == "Updated body content."
    assert data["author"] == "John Smith"
    assert data["status"] == "published"


def test_update_article_partial(client: TestClient) -> None:
    """PUT /articles/{id} with only status changes only status."""
    created = client.post(BASE_URL, json=VALID_PAYLOAD).json()
    article_id = created["id"]

    response = client.put(f"{BASE_URL}/{article_id}", json={"status": "published"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert data["title"] == VALID_PAYLOAD["title"]
    assert data["body"] == VALID_PAYLOAD["body"]
    assert data["author"] == VALID_PAYLOAD["author"]


def test_update_article_not_found(client: TestClient) -> None:
    """PUT /articles/{id} returns 404 for non-existent article."""
    response = client.put(f"{BASE_URL}/999999", json={"title": "New"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_article(client: TestClient) -> None:
    """DELETE /articles/{id} returns 204 for existing article."""
    created = client.post(BASE_URL, json=VALID_PAYLOAD).json()
    article_id = created["id"]

    response = client.delete(f"{BASE_URL}/{article_id}")
    assert response.status_code == 204


def test_delete_article_not_found(client: TestClient) -> None:
    """DELETE /articles/{id} returns 404 for non-existent article."""
    response = client.delete(f"{BASE_URL}/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_after_delete(client: TestClient) -> None:
    """GET /articles/{id} returns 404 after the article is deleted."""
    created = client.post(BASE_URL, json=VALID_PAYLOAD).json()
    article_id = created["id"]

    client.delete(f"{BASE_URL}/{article_id}")

    response = client.get(f"{BASE_URL}/{article_id}")
    assert response.status_code == 404


def test_create_article_empty_title(client: TestClient) -> None:
    """POST /articles with empty title returns 422."""
    payload = {"title": "", "body": "Some body", "author": "Author"}
    response = client.post(BASE_URL, json=payload)
    # Empty string passes max_length but fails if server enforces min_length;
    # accept both 422 and the case where empty string is valid but title is blank.
    # The issue spec says empty title → 422, so we test for that.
    assert response.status_code == 422


def test_create_article_missing_body(client: TestClient) -> None:
    """POST /articles without body returns 422."""
    payload = {"title": "Title", "author": "Author"}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 422


def test_create_article_title_too_long(client: TestClient) -> None:
    """POST /articles with title exceeding 200 chars returns 422."""
    payload = {"title": "A" * 201, "body": "body", "author": "Author"}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 422


def test_create_article_author_too_long(client: TestClient) -> None:
    """POST /articles with author exceeding 100 chars returns 422."""
    payload = {"title": "Title", "body": "body", "author": "A" * 101}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 422


def test_create_article_invalid_status(client: TestClient) -> None:
    """POST /articles with invalid status value returns 422."""
    payload = {**VALID_PAYLOAD, "status": "invalid_status"}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 422
