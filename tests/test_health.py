"""Tests for the GET /health endpoint."""

from starlette.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """Health endpoint should return HTTP 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_status_ok(client: TestClient) -> None:
    """Health endpoint should return status 'ok'."""
    response = client.get("/health")
    assert response.json()["status"] == "ok"


def test_health_has_environment(client: TestClient) -> None:
    """Health endpoint should include a non-empty 'environment' string."""
    response = client.get("/health")
    data = response.json()
    assert "environment" in data
    assert isinstance(data["environment"], str)
    assert len(data["environment"]) > 0
