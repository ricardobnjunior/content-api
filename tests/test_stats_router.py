"""Tests for the router configuration — verifies stats routes are registered."""

import os
from unittest.mock import MagicMock, patch

import pytest


def test_stats_router_imported():
    """Stats router module should be importable."""
    from app.api.endpoints.stats import router
    assert router is not None


def test_stats_router_has_routes():
    """Stats router should have at least two routes registered."""
    from app.api.endpoints.stats import router
    assert len(router.routes) >= 2


def test_main_router_includes_stats():
    """Main router should include the stats router with /stats prefix."""
    from app.api.router import router as main_router
    # Collect all route paths from the main router
    paths = []
    for route in main_router.routes:
        if hasattr(route, "path"):
            paths.append(route.path)

    # The stats prefix should appear somewhere
    stats_paths = [p for p in paths if "stats" in p]
    assert len(stats_paths) > 0, "No stats routes found in main router"


def test_main_router_still_has_articles():
    """Main router should still include articles routes."""
    from app.api.router import router as main_router
    paths = []
    for route in main_router.routes:
        if hasattr(route, "path"):
            paths.append(route.path)
    article_paths = [p for p in paths if "articles" in p]
    assert len(article_paths) > 0, "Articles routes missing from main router"


def test_main_router_still_has_categories():
    """Main router should still include categories routes."""
    from app.api.router import router as main_router
    paths = []
    for route in main_router.routes:
        if hasattr(route, "path"):
            paths.append(route.path)
    cat_paths = [p for p in paths if "categories" in p]
    assert len(cat_paths) > 0, "Categories routes missing from main router"


def test_get_stats_function_signature():
    """get_stats should accept a db parameter."""
    import inspect
    from app.api.endpoints.stats import get_stats
    sig = inspect.signature(get_stats)
    assert "db" in sig.parameters


def test_get_timeline_function_signature():
    """get_timeline should accept a db parameter."""
    import inspect
    from app.api.endpoints.stats import get_timeline
    sig = inspect.signature(get_timeline)
    assert "db" in sig.parameters


def test_stats_endpoint_get_method():
    """Stats root endpoint should use GET method."""
    from app.api.endpoints.stats import router
    root_routes = [r for r in router.routes if hasattr(r, "path") and r.path == "/"]
    assert len(root_routes) > 0
    for route in root_routes:
        assert "GET" in route.methods


def test_timeline_endpoint_get_method():
    """Timeline endpoint should use GET method."""
    from app.api.endpoints.stats import router
    timeline_routes = [
        r for r in router.routes
        if hasattr(r, "path") and "timeline" in r.path
    ]
    assert len(timeline_routes) > 0
    for route in timeline_routes:
        assert "GET" in route.methods


def test_stats_endpoint_with_mocked_db():
    """Stats endpoint should return valid structure when called with mocked DB."""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from starlette.testclient import TestClient

        db_url = f"sqlite:///{db_path}"

        with patch.dict(
            os.environ,
            {"DATABASE_URL": db_url, "SECRET_KEY": "testsecretkey"},
            clear=False,
        ):
            from app.main import app  # noqa: E402
            from app.database import get_db  # noqa: E402
            from app.models.article import Base as ArticleBase  # noqa: E402
            from app.models.category import Base as CategoryBase  # noqa: E402

            engine = create_engine(db_url, connect_args={"check_same_thread": False})
            ArticleBase.metadata.create_all(bind=engine)
            CategoryBase.metadata.create_all(bind=engine)

            TestSession = sessionmaker(bind=engine)

            def override_get_db():
                session = TestSession()
                try:
                    yield session
                finally:
                    session.close()

            app.dependency_overrides[get_db] = override_get_db

            with TestClient(app) as c:
                response = c.get("/api/v1/stats/")
                assert response.status_code == 200
                data = response.json()
                assert "total_articles" in data
                assert "by_status" in data
                assert "by_category" in data
                assert "total_categories" in data
                assert "latest_article" in data

            app.dependency_overrides.clear()
    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass
