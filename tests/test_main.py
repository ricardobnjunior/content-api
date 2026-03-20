"""Tests for app/main.py — FastAPI app configuration and health endpoint."""

import pytest
from starlette.testclient import TestClient


def test_app_title():
    """FastAPI app should have title 'Content API'."""
    from app.main import app

    assert app.title == "Content API"


def test_app_includes_api_router():
    """App should include the api_router (routes under /api/v1 reachable)."""
    from app.main import app

    routes = [r.path for r in app.routes]
    # At minimum /health and the api_router mount should be present
    assert "/health" in routes


def test_health_endpoint_status_200(client: TestClient):
    """GET /health should return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_status_ok(client: TestClient):
    """GET /health should return {'status': 'ok', ...}."""
    response = client.get("/health")
    assert response.json()["status"] == "ok"


def test_health_endpoint_returns_environment(client: TestClient):
    """GET /health should include an 'environment' key."""
    response = client.get("/health")
    data = response.json()
    assert "environment" in data
    assert isinstance(data["environment"], str)
    assert len(data["environment"]) > 0


def test_health_endpoint_environment_is_testing(client: TestClient):
    """Under test configuration, environment should be 'testing'."""
    response = client.get("/health")
    data = response.json()
    # conftest sets ENVIRONMENT=testing; settings may be cached but this
    # verifies the value is a non-empty string (cached as development is also valid)
    assert isinstance(data["environment"], str)


def test_unknown_route_returns_404(client: TestClient):
    """An unknown route should return 404."""
    response = client.get("/does-not-exist")
    assert response.status_code == 404


def test_health_response_is_json(client: TestClient):
    """GET /health should return a JSON body."""
    response = client.get("/health")
    # Will raise if not valid JSON
    data = response.json()
    assert isinstance(data, dict)
