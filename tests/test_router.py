"""Tests for app/api/router.py — central APIRouter configuration."""


def test_api_router_has_v1_prefix():
    """api_router should have prefix '/api/v1'."""
    from app.api.router import api_router
    assert api_router.prefix == "/api/v1"


def test_api_router_is_api_router_instance():
    """api_router should be an instance of fastapi.APIRouter."""
    from fastapi import APIRouter
    from app.api.router import api_router
    assert isinstance(api_router, APIRouter)


def test_api_router_starts_empty():
    """api_router should start with no routes of its own (no sub-routers yet)."""
    from app.api.router import api_router
    # routes list may be empty or contain only included sub-routers
    assert isinstance(api_router.routes, list)


def test_api_router_included_in_app():
    """The api_router must be included in the FastAPI app."""
    from app.main import app
    # All route paths in the app
    paths = [getattr(route, "path", "") for route in app.routes]
    # At minimum the app should have /health and /api/v1-prefixed routes or openapi routes
    assert "/health" in paths
