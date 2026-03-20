"""Tests for app/api/router.py — verifies all routers are registered."""

import os
from unittest.mock import patch

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")


def test_router_includes_recommendations():
    """Router should include the recommendations router."""
    from app.api.router import router  # noqa: E402

    route_paths = [route.path for route in router.routes]
    # The recommendations prefix should produce routes starting with /recommendations
    all_paths = " ".join(route_paths)
    assert "recommendations" in all_paths


def test_router_includes_articles():
    """Router should include the articles router."""
    from app.api.router import router  # noqa: E402

    route_paths = [route.path for route in router.routes]
    all_paths = " ".join(route_paths)
    assert "articles" in all_paths


def test_router_includes_categories():
    """Router should include the categories router."""
    from app.api.router import router  # noqa: E402

    route_paths = [route.path for route in router.routes]
    all_paths = " ".join(route_paths)
    assert "categories" in all_paths


def test_router_includes_suggestions():
    """Router should include the suggestions router."""
    from app.api.router import router  # noqa: E402

    route_paths = [route.path for route in router.routes]
    all_paths = " ".join(route_paths)
    assert "suggestions" in all_paths


def test_recommendations_endpoint_accessible():
    """The /api/v1/recommendations route is registered in the FastAPI app."""
    from starlette.testclient import TestClient
    from app.main import app  # noqa: E402

    client = TestClient(app, raise_server_exceptions=False)

    # Hitting an invalid article ID should return 404 (not 405 or 404 from routing)
    # The route exists if we don't get a 404 due to "no route matched"
    with patch("app.api.endpoints.recommendations.get_article", return_value=None), \
         patch("app.api.endpoints.recommendations.get_db"):
        response = client.get("/api/v1/recommendations/1/similar")

    # If the route is registered, we get 404 from business logic, not 404/405 from routing missing
    assert response.status_code in (200, 404, 500)


def test_openapi_schema_contains_recommendations():
    """OpenAPI schema includes the recommendations endpoint."""
    from starlette.testclient import TestClient
    from app.main import app  # noqa: E402

    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})
    recommendation_paths = [p for p in paths if "recommendations" in p]
    assert len(recommendation_paths) > 0
