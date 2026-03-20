"""Tests for Article CRUD REST endpoints."""

import pytest
from starlette.testclient import TestClient

from app.main import app
from app.database import get_db


@pytest.fixture()
def client(db_session):
    """Return a TestClient that uses the test db_session for all requests."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


VALID_PAYLOAD = {
    "title": "Test Article",
    "body": "This is the body of the test article.",
    "author": "Jane Doe",
}


# ---------------------------------------------------------------------------
# POST /api/v1/articles
# ---------------------------------------------------------------------------


def test_create_article_returns_201(client):
    """Creating an article with valid data returns HTTP 201."""
    response = client.post("/api/v1/articles", json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == VALID_PAYLOAD["title"]
    assert data["body"] == VALID_PAYLOAD["body"]
    assert data["author"] == VALID_PAYLOAD["author"]
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data


def test_create_article_default_status_is_draft(client):
    """When status is omitted the article defaults to draft."""
    response = client.post("/api/v1/articles", json=VALID_PAYLOAD)
    assert response.status_code == 201
    assert response.json()["status"] == "draft"


def test_create_article_explicit_published_status(client):
    """An article can be created with published status explicitly."""
    payload = {**VALID_PAYLOAD, "status": "published"}
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "published"


def test_create_article_missing_title_returns_422(client):
    """Missing title field returns HTTP 422."""
    payload = {"body": "body", "author": "author"}
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 422


def test_create_article_missing_body_returns_422(client):
    """Missing body field returns HTTP 422."""
    payload = {"title": "title", "author": "author"}
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 422


def test_create_article_missing_author_returns_422(client):
    """Missing author field returns HTTP 422."""
    payload = {"title": "title", "body": "body"}
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 422


def test_create_article_title_too_long_returns_422(client):
    """Title exceeding 200 characters returns HTTP 422."""
    payload = {**VALID_PAYLOAD, "title": "x" * 201}
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 422


def test_create_article_author_too_long_returns_422(client):
    """Author exceeding 100 characters returns HTTP 422."""
    payload = {**VALID_PAYLOAD, "author": "a" * 101}
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/articles
# ---------------------------------------------------------------------------


def test_list_articles_empty(client):
    """Empty database returns items=[] and total=0."""
    response = client.get("/api/v1/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_articles_returns_all(client):
    """After creating two articles the list contains both."""
    client.post("/api/v1/articles", json={**VALID_PAYLOAD, "title": "First"})
    client.post("/api/v1/articles", json={**VALID_PAYLOAD, "title": "Second"})
    response = client.get("/api/v1/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_articles_pagination_limit(client):
    """limit query param restricts number of returned items."""
    for i in range(5):
        client.post("/api/v1/articles", json={**VALID_PAYLOAD, "title": f"Article {i}"})
    response = client.get("/api/v1/articles?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3


def test_list_articles_pagination_skip(client):
    """skip query param offsets the returned page."""
    for i in range(4):
        client.post("/api/v1/articles", json={**VALID_PAYLOAD, "title": f"Art {i}"})
    response = client.get("/api/v1/articles?skip=2&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 2


# ---------------------------------------------------------------------------
# GET /api/v1/articles/{article_id}
# ---------------------------------------------------------------------------


def test_get_article_by_id(client):
    """Fetching an existing article by id returns 200 with correct data."""
    created = client.post("/api/v1/articles", json=VALID_PAYLOAD).json()
    article_id = created["id"]
    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == VALID_PAYLOAD["title"]


def test_get_article_not_found_returns_404(client):
    """Fetching a non-existent article returns HTTP 404."""
    response = client.get("/api/v1/articles/99999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/articles/{article_id}
# ---------------------------------------------------------------------------


def test_update_article_full(client):
    """Updating all fields returns the updated article."""
    created = client.post("/api/v1/articles", json=VALID_PAYLOAD).json()
    article_id = created["id"]
    update_payload = {
        "title": "Updated Title",
        "body": "Updated body text.",
        "author": "John Smith",
        "status": "published",
    }
    response = client.put(f"/api/v1/articles/{article_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["body"] == "Updated body text."
    assert data["author"] == "John Smith"
    assert data["status"] == "published"


def test_update_article_partial(client):
    """Updating only the title preserves all other fields."""
    created = client.post("/api/v1/articles", json=VALID_PAYLOAD).json()
    article_id = created["id"]
    response = client.put(
        f"/api/v1/articles/{article_id}", json={"title": "Only Title Changed"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Only Title Changed"
    assert data["body"] == VALID_PAYLOAD["body"]
    assert data["author"] == VALID_PAYLOAD["author"]
    assert data["status"] == "draft"


def test_update_article_status_change(client):
    """Status can be changed from draft to published via partial update."""
    created = client.post("/api/v1/articles", json=VALID_PAYLOAD).json()
    article_id = created["id"]
    response = client.put(
        f"/api/v1/articles/{article_id}", json={"status": "published"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "published"


def test_update_article_not_found_returns_404(client):
    """Updating a non-existent article returns HTTP 404."""
    response = client.put("/api/v1/articles/99999", json={"title": "nope"})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/articles/{article_id}
# ---------------------------------------------------------------------------


def test_delete_article_returns_204(client):
    """Deleting an existing article returns HTTP 204 with no body."""
    created = client.post("/api/v1/articles", json=VALID_PAYLOAD).json()
    article_id = created["id"]
    response = client.delete(f"/api/v1/articles/{article_id}")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_article_not_found_returns_404(client):
    """Deleting a non-existent article returns HTTP 404."""
    response = client.delete("/api/v1/articles/99999")
    assert response.status_code == 404


def test_get_after_delete_returns_404(client):
    """After deletion, GET on the same id returns 404."""
    created = client.post("/api/v1/articles", json=VALID_PAYLOAD).json()
    article_id = created["id"]
    client.delete(f"/api/v1/articles/{article_id}")
    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 404
