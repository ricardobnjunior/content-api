"""Verify that the main API router includes the suggestions sub-router."""

from fastapi import APIRouter

from app.api.router import router


def test_router_is_api_router_instance():
    """app.api.router.router is an APIRouter."""
    assert isinstance(router, APIRouter)


def test_router_includes_suggestions_prefix():
    """The router aggregates a sub-router with the /suggestions prefix."""
    # Collect all route paths registered on the router
    all_paths = [route.path for route in router.routes]
    # At least one route should contain 'suggestions'
    suggestions_routes = [p for p in all_paths if "suggestions" in p]
    assert suggestions_routes, (
        "No route containing 'suggestions' found in the main router. "
        f"Routes found: {all_paths}"
    )


def test_router_includes_articles_prefix():
    """The router still contains article routes (not removed by this change)."""
    all_paths = [route.path for route in router.routes]
    articles_routes = [p for p in all_paths if "articles" in p]
    assert articles_routes, (
        "No route containing 'articles' found. Existing routes may have been removed."
    )


def test_router_includes_categories_prefix():
    """The router still contains category routes (not removed by this change)."""
    all_paths = [route.path for route in router.routes]
    categories_routes = [p for p in all_paths if "categories" in p]
    assert categories_routes, (
        "No route containing 'categories' found. Existing routes may have been removed."
    )


def test_suggestions_route_has_article_id_path_param():
    """The suggestions route includes the {article_id} path parameter."""
    all_paths = [route.path for route in router.routes]
    matching = [p for p in all_paths if "suggestions" in p and "article_id" in p]
    assert matching, (
        "Expected a suggestions route with {article_id} path param. "
        f"Routes: {all_paths}"
    )
