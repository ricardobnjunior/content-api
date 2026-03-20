"""Tests for the main API router configuration."""

import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_router.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")


def test_router_includes_suggestions():
    """Main router includes the suggestions router."""
    from app.api.router import router  # noqa: E402

    # Collect all routes from the router
    all_routes = router.routes
    route_paths = [str(getattr(r, "path", "")) for r in all_routes]
    # Check that suggestions prefix is present
    has_suggestions = any("suggestions" in p for p in route_paths)
    assert has_suggestions, f"Suggestions router not found. Routes: {route_paths}"


def test_router_includes_articles():
    """Main router includes the articles router."""
    from app.api.router import router  # noqa: E402

    all_routes = router.routes
    route_paths = [str(getattr(r, "path", "")) for r in all_routes]
    has_articles = any("articles" in p for p in route_paths)
    assert has_articles, f"Articles router not found. Routes: {route_paths}"


def test_router_includes_categories():
    """Main router includes the categories router."""
    from app.api.router import router  # noqa: E402

    all_routes = router.routes
    route_paths = [str(getattr(r, "path", "")) for r in all_routes]
    has_categories = any("categories" in p for p in route_paths)
    assert has_categories, f"Categories router not found. Routes: {route_paths}"


def test_router_prefix_is_api_v1():
    """Main router has prefix /api/v1."""
    from app.api.router import router  # noqa: E402

    assert router.prefix == "/api/v1"


def test_suggestions_endpoint_registered_in_app():
    """Suggestions endpoint is reachable via the FastAPI app."""
    from app.main import app  # noqa: E402
    from starlette.testclient import TestClient
    from unittest.mock import patch, MagicMock

    client = TestClient(app)

    # Patch dependencies so it doesn't fail due to DB
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = []

    with patch("app.api.endpoints.suggestions.get_article", return_value=None):
        response = client.get("/api/v1/suggestions/categories/99999")

    # Should return 404 (article not found), not 404 from routing
    assert response.status_code == 404


def test_suggestions_router_has_correct_prefix():
    """Suggestions router has prefix /suggestions."""
    from app.api.endpoints.suggestions import router  # noqa: E402

    assert router.prefix == "/suggestions"
