"""Tests to verify app/api/router.py includes all expected routers."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_router.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-router")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key-router")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")


def test_router_has_articles_routes():
    """Main router includes articles routes."""
    from app.api.router import router  # noqa: E402

    prefixes = [route.path for route in router.routes]
    # Routes include /articles prefix
    assert any("articles" in p for p in prefixes)


def test_router_has_categories_routes():
    """Main router includes categories routes."""
    from app.api.router import router  # noqa: E402

    prefixes = [route.path for route in router.routes]
    assert any("categories" in p for p in prefixes)


def test_router_has_suggestions_routes():
    """Main router includes suggestions routes."""
    from app.api.router import router  # noqa: E402

    prefixes = [route.path for route in router.routes]
    assert any("suggestions" in p for p in prefixes)


def test_router_has_recommendations_routes():
    """Main router includes the new recommendations routes."""
    from app.api.router import router  # noqa: E402

    prefixes = [route.path for route in router.routes]
    assert any("recommendations" in p for p in prefixes)


def test_all_four_routers_present():
    """All four expected routers are mounted."""
    from app.api.router import router  # noqa: E402

    all_paths = " ".join(route.path for route in router.routes)
    assert "articles" in all_paths
    assert "categories" in all_paths
    assert "suggestions" in all_paths
    assert "recommendations" in all_paths


def test_recommendations_router_import():
    """The recommendations router can be imported without errors."""
    from app.api.endpoints.recommendations import router  # noqa: E402

    assert router is not None


def test_similarity_module_import():
    """The similarity module can be imported without errors."""
    from app.ai.similarity import find_similar_articles, _build_user_prompt  # noqa: E402

    assert callable(find_similar_articles)
    assert callable(_build_user_prompt)
