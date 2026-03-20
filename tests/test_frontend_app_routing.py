"""Tests for frontend/src/App.tsx — verifies /categories route is present."""

import os


APP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend", "src", "App.tsx"
)


def read_file():
    with open(APP_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_app_file_exists():
    """App.tsx must exist."""
    assert os.path.isfile(APP_PATH), f"Expected App.tsx at {APP_PATH}"


def test_imports_react():
    """App.tsx must import React."""
    content = read_file()
    assert "React" in content


def test_imports_router():
    """App.tsx must import routing components."""
    content = read_file()
    assert "BrowserRouter" in content or "Router" in content


def test_imports_routes_and_route():
    """App.tsx must import Routes and Route."""
    content = read_file()
    assert "Routes" in content
    assert "Route" in content


def test_categories_route_defined():
    """App.tsx must define the /categories route."""
    content = read_file()
    assert "/categories" in content


def test_imports_categories_page():
    """App.tsx must import CategoriesPage."""
    content = read_file()
    assert "CategoriesPage" in content


def test_app_component_exported():
    """App component must be exported as default."""
    content = read_file()
    assert "export default" in content
    assert "App" in content


def test_categories_page_used_in_route():
    """CategoriesPage must be used as the element in the /categories route."""
    content = read_file()
    assert "CategoriesPage" in content
    assert "element" in content
