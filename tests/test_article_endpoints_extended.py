"""Extended endpoint tests for edge cases not covered in test_articles.py."""

import pytest
from starlette.testclient import TestClient

BASE_URL = "/api/v1/articles"

VALID_PAYLOAD = {
    "title": "Extended Test Article",
    "body": "Extended body content.",
    "author": "Test Author",
}


def test_create_article_returns_id(client: TestClient) -> None:
    """POST /articles returns a positive integer ID."""
    response = client.post(BASE_URL, json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["id"] > 0


def test_create_multiple_articles_unique_ids(client: TestClient) -> None:
    """Multiple POST /articles calls produce unique IDs."""
    ids = set()
    for i in range(3):
        payload = {**VALID_PAYLOAD, "title": f"Article {i}"}
        r = client.post(BASE_URL, json=payload)
        assert r.status_code == 201
        ids.add(r.json()["id"])
    assert len(ids) == 3


def test_list_articles_structure(client: TestClient) -> None:
    """GET /articles response always has 'items' list and int 'total'."""
    r = client.get(BASE_URL)
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert "total" in body
    assert isinstance(body["items"], list)
    assert isinstance(body["total"], int)


def test_list_articles_limit_zero(client: TestClient) -> None:
    """GET /articles?limit=0 returns empty items but correct total."""
    client.post(BASE_URL, json=VALID_PAYLOAD)
    r = client.get(f"{BASE_URL}?limit=0")
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] >= 1


def test_get_article_response_fields(client: TestClient) -> None:
    """GET /articles/{id} response contains all expected fields."""
    created = client.post(BASE_URL, json=VALID_PAYLOAD).json()
    r = client.get(f"{BASE_URL}/{created['id']}")
    assert r.status_code == 200
    body = r.json()
    for field in ("id", "title", "body", "author", "status", "created_at"):
        assert field in body


def test_update_to_draft_from_published(client: TestClient) -> None:
    """PUT /articles/{id} can set status back to draft from published."""
    payload = {**VALID_PAYLOAD, "status": "published"}
    created = client.post(BASE_URL, json=payload).json()
    r = client.put(f"{BASE_URL}/{created['id']}", json={"status": "draft"})
    assert r.status_code == 200
    assert r.json()["status"] == "draft"


def test_update_nonexistent_returns_404(client: TestClient) -> None:
    """PUT /articles/0 returns 404 (ID 0 should not exist)."""
    r = client.put(f"{BASE_URL}/0", json={"title": "No article"})
    assert r.status_code == 404


def test_delete_twice_second_returns_404(client: TestClient) -> None:
    """DELETE /articles/{id} on already-deleted article returns 404."""
    created = client.post(BASE_URL, json=VALID_PAYLOAD).json()
    article_id = created["id"]
    r1 = client.delete(f"{BASE_URL}/{article_id}")
    assert r1.status_code == 204
    r2 = client.delete(f"{BASE_URL}/{article_id}")
    assert r2.status_code == 404


def test_create_article_body_single_char(client: TestClient) -> None:
    """POST /articles with body of exactly 1 character is valid."""
    payload = {"title": "Short body", "body": "X", "author": "Author"}
    r = client.post(BASE_URL, json=payload)
    assert r.status_code == 201
    assert r.json()["body"] == "X"


def test_create_article_author_single_char(client: TestClient) -> None:
    """POST /articles with author of exactly 1 character is valid."""
    payload = {"title": "Short author", "body": "Body content", "author": "Z"}
    r = client.post(BASE_URL, json=payload)
    assert r.status_code == 201
    assert r.json()["author"] == "Z"


def test_create_article_title_max_boundary(client: TestClient) -> None:
    """POST /articles with title of exactly 200 chars is valid."""
    payload = {"title": "A" * 200, "body": "body", "author": "Author"}
    r = client.post(BASE_URL, json=payload)
    assert r.status_code == 201
    assert len(r.json()["title"]) == 200


def test_get_article_non_integer_id(client: TestClient) -> None:
    """GET /articles/abc returns 422 (path param must be int)."""
    r = client.get(f"{BASE_URL}/abc")
    assert r.status_code == 422


def test_delete_article_non_integer_id(client: TestClient) -> None:
    """DELETE /articles/abc returns 422 (path param must be int)."""
    r = client.delete(f"{BASE_URL}/abc")
    assert r.status_code == 422


def test_update_body_only(client: TestClient) -> None:
    """PUT /articles/{id} with only body updates just the body."""
    created = client.post(BASE_URL, json=VALID_PAYLOAD).json()
    article_id = created["id"]
    r = client.put(f"{BASE_URL}/{article_id}", json={"body": "Brand new body."})
    assert r.status_code == 200
    data = r.json()
    assert data["body"] == "Brand new body."
    assert data["title"] == VALID_PAYLOAD["title"]
    assert data["author"] == VALID_PAYLOAD["author"]


def test_list_and_create_consistency(client: TestClient) -> None:
    """Total from GET /articles matches the number of articles created."""
    initial = client.get(BASE_URL).json()["total"]
    for i in range(4):
        client.post(BASE_URL, json={**VALID_PAYLOAD, "title": f"Batch {i}"})
    final = client.get(BASE_URL).json()["total"]
    assert final == initial + 4
