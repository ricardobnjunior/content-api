"""Tests for the health check endpoint."""

from starlette.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """Test that GET /health returns HTTP 200.

    Args:
        client: The Starlette TestClient fixture.
    """
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_contains_status_ok(client: TestClient) -> None:
    """Test that GET /health response body contains status 'ok'.

    Args:
        client: The Starlette TestClient fixture.
    """
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_response_contains_environment(client: TestClient) -> None:
    """Test that GET /health response body contains an environment key.

    Args:
        client: The Starlette TestClient fixture.
    """
    response = client.get("/health")
    data = response.json()
    assert "environment" in data


def test_health_environment_value(client: TestClient) -> None:
    """Test that the environment value matches the default setting.

    Args:
        client: The Starlette TestClient fixture.
    """
    response = client.get("/health")
    data = response.json()
    assert data["environment"] == "development"
