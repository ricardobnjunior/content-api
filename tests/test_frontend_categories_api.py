"""Tests for frontend/src/api/categories.ts"""

import os


CATEGORIES_API_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend", "src", "api", "categories.ts"
)


def read_file():
    with open(CATEGORIES_API_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_categories_api_file_exists():
    """categories.ts file must exist."""
    assert os.path.isfile(CATEGORIES_API_PATH), (
        f"Expected file at {CATEGORIES_API_PATH}"
    )


def test_imports_client():
    """Must import the shared axios client."""
    content = read_file()
    assert "from './client'" in content or 'from "./client"' in content


def test_imports_category_type():
    """Must import Category type from types/index."""
    content = read_file()
    assert "Category" in content
    assert "types/index" in content or "types'" in content or 'types"' in content


def test_get_categories_function_defined():
    """getCategories function must be exported."""
    content = read_file()
    assert "getCategories" in content
    assert "export" in content


def test_get_categories_calls_get_endpoint():
    """getCategories must call GET /api/v1/categories."""
    content = read_file()
    assert "/api/v1/categories" in content
    assert "client.get" in content


def test_create_category_function_defined():
    """createCategory function must be exported."""
    content = read_file()
    assert "createCategory" in content


def test_create_category_calls_post_endpoint():
    """createCategory must call POST /api/v1/categories."""
    content = read_file()
    assert "client.post" in content


def test_create_category_accepts_name_param():
    """createCategory must accept a name parameter."""
    content = read_file()
    assert "name" in content


def test_functions_are_async():
    """Both API functions must be async."""
    content = read_file()
    # Count async keyword occurrences — at least 2 for the two functions
    assert content.count("async function") >= 2 or content.count("async (") >= 2 or content.count("async function") + content.count("async (") >= 2


def test_returns_response_data():
    """Functions must return response.data."""
    content = read_file()
    assert "response.data" in content
