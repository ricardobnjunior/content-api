"""Tests for the health check endpoint."""

from starlette.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """Test that GET /health returns HTTP 200.

    Args:
        client: The test client fixture.
    """
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_status_ok(client: TestClient) -> None:
    """Test that GET /health response contains status ok.

    Args:
        client: The test client fixture.
    """
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_returns_environment(client: TestClient) -> None:
    """Test that GET /health response includes the environment key.

    Args:
        client: The test client fixture.
    """
    response = client.get("/health")
    data = response.json()
    assert "environment" in data
    assert isinstance(data["environment"], str)
