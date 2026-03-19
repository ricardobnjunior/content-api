"""Tests for the central API router (app/api/router.py)."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")

from fastapi import APIRouter


def test_api_router_is_api_router_instance():
    """api_router should be an instance of APIRouter."""
    from app.api.router import api_router  # noqa: E402

    assert isinstance(api_router, APIRouter)


def test_api_router_has_correct_prefix():
    """api_router should have the prefix '/api/v1'."""
    from app.api.router import api_router  # noqa: E402

    assert api_router.prefix == "/api/v1"


def test_api_router_can_include_sub_router():
    """api_router.include_router() should work without error."""
    from app.api.router import api_router  # noqa: E402

    sub = APIRouter(prefix="/test")

    @sub.get("/ping")
    def ping():
        return {"ping": "pong"}

    # Should not raise
    api_router.include_router(sub)
