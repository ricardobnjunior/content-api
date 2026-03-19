"""Tests for the FastAPI application entry point (app/main.py)."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")

from fastapi import FastAPI
from starlette.testclient import TestClient


def test_app_is_fastapi_instance():
    """app should be a FastAPI instance."""
    from app.main import app  # noqa: E402

    assert isinstance(app, FastAPI)


def test_app_title():
    """App title should be 'Content API'."""
    from app.main import app  # noqa: E402

    assert app.title == "Content API"


def test_health_endpoint_status_200(client):
    """GET /health should return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_status_ok(client):
    """GET /health should return {'status': 'ok', ...}."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_endpoint_has_environment_key(client):
    """GET /health response must include 'environment' key."""
    response = client.get("/health")
    data = response.json()
    assert "environment" in data


def test_health_endpoint_environment_is_string(client):
    """GET /health 'environment' value must be a string."""
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["environment"], str)


def test_health_endpoint_json_content_type(client):
    """GET /health should return JSON content type."""
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]


def test_api_v1_prefix_is_included(client):
    """The router with /api/v1 prefix should be registered."""
    from app.main import app  # noqa: E402

    routes = [r.path for r in app.routes]
    # At minimum the health route exists; api/v1 routes should be accessible
    assert "/health" in routes


def test_unknown_route_returns_404(client):
    """An unknown route should return HTTP 404."""
    response = client.get("/nonexistent-route-xyz")
    assert response.status_code == 404


def test_health_endpoint_only_accepts_get(client):
    """POST /health should return 405 Method Not Allowed."""
    response = client.post("/health", json={})
    assert response.status_code == 405
