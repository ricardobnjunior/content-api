"""Tests for the /health endpoint."""

from starlette.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """GET /health should return HTTP 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_status_ok(client: TestClient) -> None:
    """GET /health response body should contain status: ok."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_has_environment(client: TestClient) -> None:
    """GET /health response body should contain an environment key."""
    response = client.get("/health")
    data = response.json()
    assert "environment" in data


def test_health_environment_value(client: TestClient) -> None:
    """GET /health environment value should match the configured environment."""
    response = client.get("/health")
    data = response.json()
    # In test mode the ENVIRONMENT env var is set to "test" by conftest.py
    assert data["environment"] == "test"
