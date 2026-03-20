"""Tests for frontend component and page files."""

import os


FRONTEND_SRC = os.path.join("frontend", "src")
COMPONENTS_DIR = os.path.join(FRONTEND_SRC, "components")
PAGES_DIR = os.path.join(FRONTEND_SRC, "pages")


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ── ArticleForm.tsx ───────────────────────────────────────────────────────────

class TestArticleForm:
    filepath = os.path.join(COMPONENTS_DIR, "ArticleForm.tsx")

    def test_file_exists(self):
        assert os.path.exists(self.filepath)

    def test_imports_react(self):
        content = read_file(self.filepath)
        assert "React" in content

    def test_exports_default(self):
        content = read_file(self.filepath)
        assert "export default" in content
        assert "ArticleForm" in content

    def test_has_article_form_props_interface(self):
        content = read_file(self.filepath)
        assert "ArticleFormProps" in content

    def test_initial_data_prop(self):
        content = read_file(self.filepath)
        assert "initialData" in content

    def test_on_submit_prop(self):
        content = read_file(self.filepath)
        assert "onSubmit" in content

    def test_is_submitting_prop(self):
        content = read_file(self.filepath)
        assert "isSubmitting" in content

    def test_server_error_prop(self):
        content = read_file(self.filepath)
        assert "serverError" in content

    def test_title_field(self):
        content = read_file(self.filepath)
        assert "article-title" in content or "title" in content

    def test_content_textarea(self):
        content = read_file(self.filepath)
        assert "textarea" in content
        assert "article-content" in content or "content" in content

    def test_status_select(self):
        content = read_file(self.filepath)
        assert "select" in content
        assert "draft" in content
        assert "published" in content

    def test_categories_section(self):
        content = read_file(self.filepath)
        assert "Categories" in content
        assert "getCategories" in content

    def test_loads_categories_on_mount(self):
        content = read_file(self.filepath)
        assert "useEffect" in content
        assert "getCategories" in content

    def test_checkbox_category_selection(self):
        content = read_file(self.filepath)
        assert "checkbox" in content

    def test_submit_button_disabled_when_title_empty(self):
        content = read_file(self.filepath)
        assert "title.trim()" in content

    def test_handle_submit_prevents_default(self):
        content = read_file(self.filepath)
        assert "preventDefault" in content

    def test_aria_attributes(self):
        content = read_file(self.filepath)
        assert "aria-label" in content

    def test_uses_use_state(self):
        content = read_file(self.filepath)
        assert "useState" in content

    def test_category_change_handler(self):
        content = read_file(self.filepath)
        assert "handleCategoryChange" in content


# ── ArticleCreatePage.tsx ─────────────────────────────────────────────────────

class TestArticleCreatePage:
    filepath = os.path.join(PAGES_DIR, "ArticleCreatePage.tsx")

    def test_file_exists(self):
        assert os.path.exists(self.filepath)

    def test_exports_default(self):
        content = read_file(self.filepath)
        assert "export default" in content
        assert "ArticleCreatePage" in content

    def test_imports_article_form(self):
        content = read_file(self.filepath)
        assert "ArticleForm" in content

    def test_imports_create_article(self):
        content = read_file(self.filepath)
        assert "createArticle" in content

    def test_uses_navigate(self):
        content = read_file(self.filepath)
        assert "useNavigate" in content

    def test_redirects_on_success(self):
        content = read_file(self.filepath)
        assert "navigate" in content
        assert "/articles/" in content

    def test_handles_server_error(self):
        content = read_file(self.filepath)
        assert "serverError" in content

    def test_extract_error_message_function(self):
        content = read_file(self.filepath)
        assert "extractErrorMessage" in content

    def test_has_heading(self):
        content = read_file(self.filepath)
        assert "Create" in content

    def test_manages_submitting_state(self):
        content = read_file(self.filepath)
        assert "isSubmitting" in content
        assert "setIsSubmitting" in content


# ── ArticleEditPage.tsx ───────────────────────────────────────────────────────

class TestArticleEditPage:
    filepath = os.path.join(PAGES_DIR, "ArticleEditPage.tsx")

    def test_file_exists(self):
        assert os.path.exists(self.filepath)

    def test_exports_default(self):
        content = read_file(self.filepath)
        assert "export default" in content
        assert "ArticleEditPage" in content

    def test_imports_article_form(self):
        content = read_file(self.filepath)
        assert "ArticleForm" in content

    def test_uses_params(self):
        content = read_file(self.filepath)
        assert "useParams" in content

    def test_uses_navigate(self):
        content = read_file(self.filepath)
        assert "useNavigate" in content

    def test_fetches_article_on_mount(self):
        content = read_file(self.filepath)
        assert "getArticle" in content
        assert "useEffect" in content

    def test_calls_update_article(self):
        content = read_file(self.filepath)
        assert "updateArticle" in content

    def test_redirects_after_update(self):
        content = read_file(self.filepath)
        assert "navigate" in content
        assert "/articles/" in content

    def test_shows_loading_state(self):
        content = read_file(self.filepath)
        assert "Loading" in content or "loading" in content

    def test_shows_load_error(self):
        content = read_file(self.filepath)
        assert "loadError" in content or "Failed to load" in content

    def test_passes_initial_data_to_form(self):
        content = read_file(self.filepath)
        assert "initialData" in content

    def test_has_heading(self):
        content = read_file(self.filepath)
        assert "Edit" in content

    def test_handles_missing_id(self):
        content = read_file(self.filepath)
        assert "if (!id)" in content

    def test_back_to_articles_button_on_error(self):
        content = read_file(self.filepath)
        assert "/articles" in content


# ── ArticleDetailPage.tsx ─────────────────────────────────────────────────────

class TestArticleDetailPage:
    filepath = os.path.join(PAGES_DIR, "ArticleDetailPage.tsx")

    def test_file_exists(self):
        assert os.path.exists(self.filepath)

    def test_exports_default(self):
        content = read_file(self.filepath)
        assert "export default" in content
        assert "ArticleDetailPage" in content

    def test_uses_params(self):
        content = read_file(self.filepath)
        assert "useParams" in content

    def test_uses_navigate(self):
        content = read_file(self.filepath)
        assert "useNavigate" in content

    def test_fetches_article(self):
        content = read_file(self.filepath)
        assert "getArticle" in content

    def test_has_edit_button(self):
        content = read_file(self.filepath)
        assert "Edit" in content
        assert "handleEdit" in content

    def test_has_delete_button(self):
        content = read_file(self.filepath)
        assert "Delete" in content
        assert "handleDelete" in content

    def test_delete_uses_confirm(self):
        content = read_file(self.filepath)
        assert "window.confirm" in content

    def test_delete_calls_delete_article(self):
        content = read_file(self.filepath)
        assert "deleteArticle" in content

    def test_redirects_after_delete(self):
        content = read_file(self.filepath)
        assert 'navigate("/articles")' in content

    def test_shows_article_status(self):
        content = read_file(self.filepath)
        assert "status" in content
        assert "Status" in content

    def test_shows_categories(self):
        content = read_file(self.filepath)
        assert "categories" in content or "Categories" in content

    def test_shows_loading_state(self):
        content = read_file(self.filepath)
        assert "Loading" in content or "loading" in content

    def test_shows_error_state(self):
        content = read_file(self.filepath)
        assert "role=\"alert\"" in content

    def test_back_to_articles_navigation(self):
        content = read_file(self.filepath)
        assert "/articles" in content

    def test_is_deleting_state(self):
        content = read_file(self.filepath)
        assert "isDeleting" in content
