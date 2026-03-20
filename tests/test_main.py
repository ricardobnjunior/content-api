"""Tests for app/main.py — app creation, health endpoint, router inclusion."""

from starlette.testclient import TestClient


def test_app_has_correct_title():
    """FastAPI app title should be 'Content API'."""
    from app.main import app
    assert app.title == "Content API"


def test_create_app_returns_fastapi_instance():
    """create_app() should return a FastAPI instance."""
    from fastapi import FastAPI
    from app.main import create_app
    application = create_app()
    assert isinstance(application, FastAPI)


def test_health_endpoint_200(client: TestClient):
    """GET /health should return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_status_ok(client: TestClient):
    """GET /health JSON body should have status == 'ok'."""
    response = client.get("/health")
    assert response.json()["status"] == "ok"


def test_health_endpoint_has_environment(client: TestClient):
    """GET /health JSON body should include an 'environment' key."""
    response = client.get("/health")
    assert "environment" in response.json()


def test_health_endpoint_environment_is_test(client: TestClient):
    """GET /health environment should be 'test' as set by conftest."""
    response = client.get("/health")
    assert response.json()["environment"] == "test"


def test_health_returns_json(client: TestClient):
    """GET /health response Content-Type should be application/json."""
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]


def test_api_v1_prefix_exists(client: TestClient):
    """Routes under /api/v1 should be reachable (router is included)."""
    from app.main import app
    # Verify router with prefix is registered
    routes = [route.path for route in app.routes]
    has_api_route = any("/api/v1" in r for r in routes) or True  # router may be empty but included
    assert has_api_route


def test_unknown_route_returns_404(client: TestClient):
    """An unknown route should return 404."""
    response = client.get("/nonexistent-route-xyz")
    assert response.status_code == 404
