"""Tests for frontend/src/components/CategoryList.tsx"""

import os


CATEGORY_LIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend", "src", "components", "CategoryList.tsx"
)


def read_file():
    with open(CATEGORY_LIST_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_category_list_file_exists():
    """CategoryList.tsx must exist."""
    assert os.path.isfile(CATEGORY_LIST_PATH), (
        f"Expected file at {CATEGORY_LIST_PATH}"
    )


def test_imports_react():
    """Must import React."""
    content = read_file()
    assert "React" in content
    assert "import" in content


def test_imports_category_type():
    """Must import Category type."""
    content = read_file()
    assert "Category" in content


def test_component_defined():
    """CategoryList component must be defined."""
    content = read_file()
    assert "CategoryList" in content


def test_component_exported_as_default():
    """CategoryList must be exported as default."""
    content = read_file()
    assert "export default" in content


def test_renders_empty_state_message():
    """Must show 'No categories yet' when list is empty."""
    content = read_file()
    assert "No categories yet" in content


def test_renders_table():
    """Must render a table element for categories."""
    content = read_file()
    assert "<table" in content


def test_renders_name_column():
    """Must display category name."""
    content = read_file()
    assert "Name" in content
    assert "category.name" in content or "{category.name}" in content


def test_renders_articles_column():
    """Must display an articles/article count column."""
    content = read_file()
    assert "Articles" in content or "articleCount" in content


def test_accepts_categories_prop():
    """Must accept a categories prop."""
    content = read_file()
    assert "categories" in content


def test_maps_over_categories():
    """Must iterate over categories to render rows."""
    content = read_file()
    assert ".map(" in content


def test_uses_category_id_as_key():
    """Must use category.id as key in list rendering."""
    content = read_file()
    assert "category.id" in content or "key={category" in content
