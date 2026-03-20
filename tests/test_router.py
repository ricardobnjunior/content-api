"""Tests for app/api/router.py — central API router."""

from fastapi import APIRouter
from fastapi.routing import APIRoute


def test_api_router_is_apirouter_instance():
    """api_router should be an APIRouter instance."""
    from app.api.router import api_router

    assert isinstance(api_router, APIRouter)


def test_api_router_has_correct_prefix():
    """api_router should have prefix '/api/v1'."""
    from app.api.router import api_router

    assert api_router.prefix == "/api/v1"


def test_api_router_importable():
    """api_router should be importable without errors."""
    try:
        from app.api.router import api_router  # noqa: F401
    except ImportError as exc:
        pytest.fail(f"Could not import api_router: {exc}")


import pytest  # noqa: E402 — needed for pytest.fail above
