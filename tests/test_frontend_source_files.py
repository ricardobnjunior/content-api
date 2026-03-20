"""
Tests for frontend TypeScript/TSX source files.
Verifies that key source files exist and contain expected patterns.
"""

import os


FRONTEND_SRC = os.path.join(os.path.dirname(__file__), "..", "frontend", "src")


def read_src(relative_path: str) -> str:
    full_path = os.path.join(FRONTEND_SRC, relative_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def src_path(relative_path: str) -> str:
    return os.path.join(FRONTEND_SRC, relative_path)


# ---------------------------------------------------------------------------
# App.tsx tests
# ---------------------------------------------------------------------------

def test_app_tsx_exists():
    assert os.path.isfile(src_path("App.tsx"))


def test_app_tsx_has_browser_router():
    content = read_src("App.tsx")
    assert "BrowserRouter" in content


def test_app_tsx_has_routes():
    content = read_src("App.tsx")
    assert "Routes" in content


def test_app_tsx_has_route():
    content = read_src("App.tsx")
    assert "Route" in content


def test_app_tsx_has_home_route():
    content = read_src("App.tsx")
    assert 'path="/"' in content


def test_app_tsx_has_articles_route():
    content = read_src("App.tsx")
    assert "/articles" in content


def test_app_tsx_has_categories_route():
    content = read_src("App.tsx")
    assert "/categories" in content


def test_app_tsx_imports_layout():
    content = read_src("App.tsx")
    assert "Layout" in content


def test_app_tsx_imports_home_page():
    content = read_src("App.tsx")
    assert "HomePage" in content


# ---------------------------------------------------------------------------
# api/client.ts tests
# ---------------------------------------------------------------------------

def test_api_client_ts_exists():
    assert os.path.isfile(src_path("api/client.ts"))


def test_api_client_has_base_url():
    content = read_src("api/client.ts")
    assert "/api/v1" in content


def test_api_client_uses_axios():
    content = read_src("api/client.ts")
    assert "axios" in content


def test_api_client_has_create_call():
    content = read_src("api/client.ts")
    assert "axios.create" in content


def test_api_client_has_error_interceptor():
    content = read_src("api/client.ts")
    assert "interceptors" in content


def test_api_client_exports_default():
    content = read_src("api/client.ts")
    assert "export default" in content


# ---------------------------------------------------------------------------
# types/index.ts tests
# ---------------------------------------------------------------------------

def test_types_index_ts_exists():
    assert os.path.isfile(src_path("types/index.ts"))


def test_types_has_article_interface():
    content = read_src("types/index.ts")
    assert "Article" in content


def test_types_article_has_id_field():
    content = read_src("types/index.ts")
    assert "id: number" in content


def test_types_article_has_title_field():
    content = read_src("types/index.ts")
    assert "title: string" in content


def test_types_article_has_status_field():
    content = read_src("types/index.ts")
    assert "status: string" in content


def test_types_article_has_created_at_field():
    content = read_src("types/index.ts")
    assert "created_at: string" in content


def test_types_has_pagination_meta():
    content = read_src("types/index.ts")
    assert "PaginationMeta" in content


def test_types_pagination_meta_has_total():
    content = read_src("types/index.ts")
    assert "total: number" in content


def test_types_pagination_meta_has_page():
    content = read_src("types/index.ts")
    assert "page: number" in content


def test_types_pagination_meta_has_per_page():
    content = read_src("types/index.ts")
    assert "per_page: number" in content


def test_types_pagination_meta_has_total_pages():
    content = read_src("types/index.ts")
    assert "total_pages: number" in content


def test_types_has_article_list():
    content = read_src("types/index.ts")
    assert "ArticleList" in content


def test_types_has_category_interface():
    content = read_src("types/index.ts")
    assert "Category" in content


def test_types_category_has_name_field():
    content = read_src("types/index.ts")
    assert "name: string" in content


# ---------------------------------------------------------------------------
# components/Layout.tsx tests
# ---------------------------------------------------------------------------

def test_layout_tsx_exists():
    assert os.path.isfile(src_path("components/Layout.tsx"))


def test_layout_has_nav_links():
    content = read_src("components/Layout.tsx")
    assert "Link" in content


def test_layout_has_home_link():
    content = read_src("components/Layout.tsx")
    assert 'to="/"' in content


def test_layout_has_articles_link():
    content = read_src("components/Layout.tsx")
    assert "/articles" in content


def test_layout_has_categories_link():
    content = read_src("components/Layout.tsx")
    assert "/categories" in content


def test_layout_renders_children():
    content = read_src("components/Layout.tsx")
    assert "children" in content


# ---------------------------------------------------------------------------
# pages/HomePage.tsx tests
# ---------------------------------------------------------------------------

def test_home_page_tsx_exists():
    assert os.path.isfile(src_path("pages/HomePage.tsx"))


def test_home_page_has_navigation_links():
    content = read_src("pages/HomePage.tsx")
    assert "Link" in content


def test_home_page_links_to_articles():
    content = read_src("pages/HomePage.tsx")
    assert "/articles" in content


def test_home_page_links_to_categories():
    content = read_src("pages/HomePage.tsx")
    assert "/categories" in content


def test_home_page_exports_default():
    content = read_src("pages/HomePage.tsx")
    assert "export default" in content


# ---------------------------------------------------------------------------
# main.tsx tests
# ---------------------------------------------------------------------------

def test_main_tsx_exists():
    assert os.path.isfile(src_path("main.tsx"))


def test_main_tsx_creates_root():
    content = read_src("main.tsx")
    assert "createRoot" in content


def test_main_tsx_renders_app():
    content = read_src("main.tsx")
    assert "App" in content


def test_main_tsx_has_strict_mode():
    content = read_src("main.tsx")
    assert "StrictMode" in content
