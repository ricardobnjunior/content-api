"""Tests for types/index.ts and App.tsx routing."""

import os


FRONTEND_SRC = os.path.join("frontend", "src")


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ── types/index.ts ────────────────────────────────────────────────────────────

class TestTypes:
    filepath = os.path.join(FRONTEND_SRC, "types", "index.ts")

    def test_file_exists(self):
        assert os.path.exists(self.filepath)

    def test_article_interface(self):
        content = read_file(self.filepath)
        assert "Article" in content
        assert "id" in content
        assert "title" in content
        assert "status" in content

    def test_article_create_interface(self):
        content = read_file(self.filepath)
        assert "ArticleCreate" in content

    def test_article_update_interface(self):
        content = read_file(self.filepath)
        assert "ArticleUpdate" in content

    def test_category_interface(self):
        content = read_file(self.filepath)
        assert "Category" in content
        assert "slug" in content

    def test_article_list_params(self):
        content = read_file(self.filepath)
        assert "ArticleListParams" in content

    def test_article_list_response(self):
        content = read_file(self.filepath)
        assert "ArticleListResponse" in content
        assert "items" in content
        assert "total" in content

    def test_status_union_type(self):
        content = read_file(self.filepath)
        assert "draft" in content
        assert "published" in content

    def test_category_ids_optional(self):
        content = read_file(self.filepath)
        assert "category_ids" in content

    def test_exports_all_interfaces(self):
        content = read_file(self.filepath)
        assert "export interface Article" in content
        assert "export interface ArticleCreate" in content
        assert "export interface ArticleUpdate" in content
        assert "export interface Category" in content


# ── App.tsx routing ───────────────────────────────────────────────────────────

class TestAppRouting:
    filepath = os.path.join(FRONTEND_SRC, "App.tsx")

    def test_file_exists(self):
        assert os.path.exists(self.filepath)

    def test_imports_react_router(self):
        content = read_file(self.filepath)
        assert "react-router-dom" in content

    def test_has_articles_list_route(self):
        content = read_file(self.filepath)
        assert "/articles" in content

    def test_has_article_create_route(self):
        content = read_file(self.filepath)
        assert "/articles/new" in content

    def test_has_article_detail_route(self):
        content = read_file(self.filepath)
        assert "/articles/:id" in content

    def test_has_article_edit_route(self):
        content = read_file(self.filepath)
        assert "/articles/:id/edit" in content

    def test_imports_create_page(self):
        content = read_file(self.filepath)
        assert "ArticleCreatePage" in content

    def test_imports_edit_page(self):
        content = read_file(self.filepath)
        assert "ArticleEditPage" in content

    def test_imports_detail_page(self):
        content = read_file(self.filepath)
        assert "ArticleDetailPage" in content

    def test_imports_list_page(self):
        content = read_file(self.filepath)
        assert "ArticleListPage" in content

    def test_uses_browser_router(self):
        content = read_file(self.filepath)
        assert "BrowserRouter" in content or "Router" in content

    def test_uses_routes_component(self):
        content = read_file(self.filepath)
        assert "Routes" in content
        assert "Route" in content

    def test_create_route_before_id_route(self):
        # /articles/new must appear before /articles/:id to avoid routing conflicts
        content = read_file(self.filepath)
        new_pos = content.find("/articles/new")
        id_pos = content.find("/articles/:id")
        assert new_pos != -1, "/articles/new route not found"
        assert id_pos != -1, "/articles/:id route not found"
        assert new_pos < id_pos, "/articles/new must come before /articles/:id"

    def test_exports_default_app(self):
        content = read_file(self.filepath)
        assert "export default" in content
        assert "App" in content
