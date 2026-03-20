"""Tests for frontend API files (articles.ts, categories.ts, client.ts)."""

import os


FRONTEND_SRC = os.path.join("frontend", "src")
API_DIR = os.path.join(FRONTEND_SRC, "api")


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ── articles.ts ──────────────────────────────────────────────────────────────

class TestArticlesApi:
    filepath = os.path.join(API_DIR, "articles.ts")

    def test_file_exists(self):
        assert os.path.exists(self.filepath), f"Missing: {self.filepath}"

    def test_imports_client(self):
        content = read_file(self.filepath)
        assert "import client from" in content

    def test_imports_types(self):
        content = read_file(self.filepath)
        assert "ArticleCreate" in content
        assert "ArticleUpdate" in content
        assert "ArticleListParams" in content
        assert "ArticleListResponse" in content

    def test_get_articles_function(self):
        content = read_file(self.filepath)
        assert "getArticles" in content
        assert "/articles" in content

    def test_get_article_function(self):
        content = read_file(self.filepath)
        assert "getArticle" in content
        assert "articles/${id}" in content or "articles/" in content

    def test_create_article_function(self):
        content = read_file(self.filepath)
        assert "createArticle" in content
        assert "client.post" in content

    def test_update_article_function(self):
        content = read_file(self.filepath)
        assert "updateArticle" in content
        assert "client.put" in content

    def test_delete_article_function(self):
        content = read_file(self.filepath)
        assert "deleteArticle" in content
        assert "client.delete" in content

    def test_get_article_uses_id_in_url(self):
        content = read_file(self.filepath)
        assert "/articles/${id}" in content or "`/articles/${id}`" in content

    def test_delete_returns_void(self):
        content = read_file(self.filepath)
        assert "Promise<void>" in content


# ── categories.ts ─────────────────────────────────────────────────────────────

class TestCategoriesApi:
    filepath = os.path.join(API_DIR, "categories.ts")

    def test_file_exists(self):
        assert os.path.exists(self.filepath)

    def test_get_categories_function(self):
        content = read_file(self.filepath)
        assert "getCategories" in content
        assert "/categories" in content

    def test_imports_category_type(self):
        content = read_file(self.filepath)
        assert "Category" in content


# ── client.ts ─────────────────────────────────────────────────────────────────

class TestApiClient:
    filepath = os.path.join(API_DIR, "client.ts")

    def test_file_exists(self):
        assert os.path.exists(self.filepath)

    def test_uses_axios(self):
        content = read_file(self.filepath)
        assert "axios" in content

    def test_base_url(self):
        content = read_file(self.filepath)
        assert "/api/v1" in content

    def test_exports_default(self):
        content = read_file(self.filepath)
        assert "export default" in content
