"""Tests for frontend/src/pages/CategoriesPage.tsx"""

import os


CATEGORIES_PAGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend", "src", "pages", "CategoriesPage.tsx"
)


def read_file():
    with open(CATEGORIES_PAGE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_categories_page_file_exists():
    """CategoriesPage.tsx must exist."""
    assert os.path.isfile(CATEGORIES_PAGE_PATH), (
        f"Expected file at {CATEGORIES_PAGE_PATH}"
    )


def test_imports_react_hooks():
    """Must import useState and useEffect from React."""
    content = read_file()
    assert "useState" in content
    assert "useEffect" in content


def test_imports_get_categories():
    """Must import getCategories API function."""
    content = read_file()
    assert "getCategories" in content


def test_imports_create_category():
    """Must import createCategory API function."""
    content = read_file()
    assert "createCategory" in content


def test_imports_category_list_component():
    """Must import CategoryList component."""
    content = read_file()
    assert "CategoryList" in content


def test_component_exported_as_default():
    """CategoriesPage must be exported as default."""
    content = read_file()
    assert "export default" in content
    assert "CategoriesPage" in content


def test_has_form_for_creating_category():
    """Must render a form element."""
    content = read_file()
    assert "<form" in content


def test_has_text_input():
    """Must have a text input for category name."""
    content = read_file()
    assert 'type="text"' in content or "type='text'" in content


def test_has_submit_button():
    """Must have a submit/Add button."""
    content = read_file()
    assert "Add" in content
    assert "<button" in content


def test_shows_loading_state():
    """Must show a loading indicator while fetching."""
    content = read_file()
    assert "loading" in content.lower()
    assert "Loading" in content or "loading" in content


def test_shows_error_state():
    """Must handle and display errors."""
    content = read_file()
    assert "error" in content
    assert "Failed" in content or "error" in content


def test_clears_input_after_submit():
    """Must clear input (setNewName to empty string) after successful create."""
    content = read_file()
    assert "setNewName" in content
    assert "''" in content or '""' in content


def test_prepends_new_category_to_list():
    """Must prepend new category to categories list."""
    content = read_file()
    assert "setCategories" in content
    # Should use spread or prepend pattern
    assert "prev" in content or "created" in content


def test_handles_form_submit():
    """Must have onSubmit handler."""
    content = read_file()
    assert "onSubmit" in content or "handleSubmit" in content


def test_uses_category_list_component():
    """Must render CategoryList component."""
    content = read_file()
    assert "<CategoryList" in content


def test_validates_empty_input():
    """Must guard against empty name submission."""
    content = read_file()
    assert "trim()" in content


def test_cancels_fetch_on_unmount():
    """Must handle component unmount (cleanup) in useEffect."""
    content = read_file()
    assert "cancelled" in content or "cancel" in content or "return () =>" in content


def test_disabled_button_when_submitting():
    """Submit button must be disabled during submission."""
    content = read_file()
    assert "disabled" in content
    assert "submitting" in content
