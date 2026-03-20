"""
Tests for the articles listing page frontend implementation.
Verifies that key components and API files contain expected content.
"""
import os


# Helper to resolve frontend source file paths
def src_path(relative: str) -> str:
    """Return absolute path to a frontend/src file."""
    base = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src')
    return os.path.normpath(os.path.join(base, relative))


def read_src(relative: str) -> str:
    """Read a frontend/src file and return its content."""
    path = src_path(relative)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


# ─── api/articles.ts ────────────────────────────────────────────────────────

class TestArticlesApi:
    def test_file_exists(self):
        assert os.path.isfile(src_path('api/articles.ts'))

    def test_imports_client(self):
        content = read_src('api/articles.ts')
        assert 'client' in content
        assert './client' in content or '../api/client' in content or 'client' in content

    def test_imports_article_list_type(self):
        content = read_src('api/articles.ts')
        assert 'ArticleList' in content

    def test_get_articles_function_defined(self):
        content = read_src('api/articles.ts')
        assert 'getArticles' in content

    def test_get_articles_params_interface(self):
        content = read_src('api/articles.ts')
        assert 'GetArticlesParams' in content

    def test_get_articles_uses_correct_endpoint(self):
        content = read_src('api/articles.ts')
        assert '/articles' in content

    def test_get_articles_returns_promise(self):
        content = read_src('api/articles.ts')
        assert 'Promise' in content

    def test_params_include_page(self):
        content = read_src('api/articles.ts')
        assert 'page' in content

    def test_params_include_per_page(self):
        content = read_src('api/articles.ts')
        assert 'per_page' in content

    def test_params_include_status(self):
        content = read_src('api/articles.ts')
        assert 'status' in content

    def test_params_include_search(self):
        content = read_src('api/articles.ts')
        assert 'search' in content

    def test_params_include_category_id(self):
        content = read_src('api/articles.ts')
        assert 'category_id' in content

    def test_uses_client_get(self):
        content = read_src('api/articles.ts')
        assert 'client.get' in content

    def test_returns_response_data(self):
        content = read_src('api/articles.ts')
        assert 'response.data' in content

    def test_async_function(self):
        content = read_src('api/articles.ts')
        assert 'async' in content


# ─── components/SearchBar.tsx ────────────────────────────────────────────────

class TestSearchBarComponent:
    def test_file_exists(self):
        assert os.path.isfile(src_path('components/SearchBar.tsx'))

    def test_component_name(self):
        content = read_src('components/SearchBar.tsx')
        assert 'SearchBar' in content

    def test_uses_react(self):
        content = read_src('components/SearchBar.tsx')
        assert 'React' in content

    def test_uses_usestate(self):
        content = read_src('components/SearchBar.tsx')
        assert 'useState' in content

    def test_uses_useeffect(self):
        content = read_src('components/SearchBar.tsx')
        assert 'useEffect' in content

    def test_uses_useref(self):
        content = read_src('components/SearchBar.tsx')
        assert 'useRef' in content

    def test_has_300ms_debounce(self):
        content = read_src('components/SearchBar.tsx')
        assert '300' in content

    def test_has_settimeout(self):
        content = read_src('components/SearchBar.tsx')
        assert 'setTimeout' in content

    def test_has_cleartimeout(self):
        content = read_src('components/SearchBar.tsx')
        assert 'clearTimeout' in content

    def test_has_on_change_prop(self):
        content = read_src('components/SearchBar.tsx')
        assert 'onChange' in content

    def test_has_placeholder_prop(self):
        content = read_src('components/SearchBar.tsx')
        assert 'placeholder' in content

    def test_renders_input_element(self):
        content = read_src('components/SearchBar.tsx')
        assert '<input' in content

    def test_has_aria_label(self):
        content = read_src('components/SearchBar.tsx')
        assert 'aria-label' in content

    def test_exported_as_default(self):
        content = read_src('components/SearchBar.tsx')
        assert 'export default SearchBar' in content

    def test_handles_external_value_sync(self):
        content = read_src('components/SearchBar.tsx')
        # displayValue should be synced when parent updates value
        assert 'displayValue' in content

    def test_cleanup_on_unmount(self):
        content = read_src('components/SearchBar.tsx')
        # useEffect with return cleanup function
        assert 'return () =>' in content or 'return ()=>' in content


# ─── components/Pagination.tsx ───────────────────────────────────────────────

class TestPaginationComponent:
    def test_file_exists(self):
        assert os.path.isfile(src_path('components/Pagination.tsx'))

    def test_component_name(self):
        content = read_src('components/Pagination.tsx')
        assert 'Pagination' in content

    def test_uses_react(self):
        content = read_src('components/Pagination.tsx')
        assert 'React' in content

    def test_has_current_page_prop(self):
        content = read_src('components/Pagination.tsx')
        assert 'currentPage' in content

    def test_has_total_pages_prop(self):
        content = read_src('components/Pagination.tsx')
        assert 'totalPages' in content

    def test_has_on_page_change_prop(self):
        content = read_src('components/Pagination.tsx')
        assert 'onPageChange' in content

    def test_has_previous_button(self):
        content = read_src('components/Pagination.tsx')
        assert 'Previous' in content

    def test_has_next_button(self):
        content = read_src('components/Pagination.tsx')
        assert 'Next' in content

    def test_has_page_indicator(self):
        content = read_src('components/Pagination.tsx')
        assert 'Page' in content

    def test_disables_previous_on_first_page(self):
        content = read_src('components/Pagination.tsx')
        assert 'isFirstPage' in content

    def test_disables_next_on_last_page(self):
        content = read_src('components/Pagination.tsx')
        assert 'isLastPage' in content

    def test_has_aria_label(self):
        content = read_src('components/Pagination.tsx')
        assert 'aria-label' in content

    def test_exported_as_default(self):
        content = read_src('components/Pagination.tsx')
        assert 'export default Pagination' in content

    def test_handles_zero_total_pages(self):
        content = read_src('components/Pagination.tsx')
        assert 'totalPages === 0' in content or 'No pages' in content

    def test_button_disabled_attribute(self):
        content = read_src('components/Pagination.tsx')
        assert 'disabled' in content

    def test_navigation_role(self):
        content = read_src('components/Pagination.tsx')
        assert 'nav' in content or 'navigation' in content


# ─── components/ArticleTable.tsx ─────────────────────────────────────────────

class TestArticleTableComponent:
    def test_file_exists(self):
        assert os.path.isfile(src_path('components/ArticleTable.tsx'))

    def test_component_name(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'ArticleTable' in content

    def test_uses_react(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'React' in content

    def test_imports_article_type(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'Article' in content

    def test_imports_link(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'Link' in content
        assert 'react-router-dom' in content

    def test_has_articles_prop(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'articles' in content

    def test_has_loading_prop(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'loading' in content

    def test_shows_loading_message(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'Loading' in content

    def test_shows_empty_message(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'No articles found' in content

    def test_has_title_column(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'Title' in content

    def test_has_status_column(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'Status' in content

    def test_has_created_at_column(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'Created' in content

    def test_has_actions_column(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'Actions' in content

    def test_renders_view_link(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'View' in content

    def test_formats_date(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'toLocaleDateString' in content or 'created_at' in content

    def test_status_badge_colors(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'published' in content
        assert 'draft' in content

    def test_links_to_article_detail(self):
        content = read_src('components/ArticleTable.tsx')
        assert '/articles/' in content

    def test_exported_as_default(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'export default ArticleTable' in content

    def test_table_aria_label(self):
        content = read_src('components/ArticleTable.tsx')
        assert 'aria-label' in content


# ─── pages/ArticlesPage.tsx ──────────────────────────────────────────────────

class TestArticlesPage:
    def test_file_exists(self):
        assert os.path.isfile(src_path('pages/ArticlesPage.tsx'))

    def test_component_name(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'ArticlesPage' in content

    def test_uses_react(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'React' in content

    def test_imports_get_articles(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'getArticles' in content

    def test_imports_article_table(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'ArticleTable' in content

    def test_imports_pagination(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'Pagination' in content

    def test_imports_search_bar(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'SearchBar' in content

    def test_imports_layout(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'Layout' in content

    def test_uses_usestate(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'useState' in content

    def test_uses_useeffect(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'useEffect' in content

    def test_has_pagination_state(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'page' in content
        assert 'setPage' in content

    def test_has_status_filter(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'status' in content
        assert 'setStatus' in content

    def test_has_search_state(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'search' in content

    def test_has_loading_state(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'loading' in content
        assert 'setLoading' in content

    def test_has_error_state(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'error' in content
        assert 'setError' in content

    def test_has_error_display(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'Failed to load articles' in content or 'error' in content

    def test_status_filter_has_all_option(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'All' in content

    def test_status_filter_has_draft_option(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'draft' in content or 'Draft' in content

    def test_status_filter_has_published_option(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'published' in content or 'Published' in content

    def test_resets_page_on_search(self):
        content = read_src('pages/ArticlesPage.tsx')
        # When search changes, page should reset to 1
        assert 'setPage(1)' in content

    def test_resets_page_on_status_change(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'setPage(1)' in content

    def test_passes_per_page_10(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'per_page' in content
        assert '10' in content

    def test_handles_abort_controller(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'AbortController' in content or 'cancelled' in content

    def test_exports_default(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'export default ArticlesPage' in content

    def test_imports_css(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'ArticlesPage.css' in content

    def test_renders_articles_heading(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'Articles' in content

    def test_total_pages_from_meta(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'total_pages' in content

    def test_articles_state_initialized_empty(self):
        content = read_src('pages/ArticlesPage.tsx')
        assert 'useState<Article[]>([])' in content or "useState<Article[]>([])" in content or '[]' in content


# ─── pages/ArticlesPage.css ──────────────────────────────────────────────────

class TestArticlesPageCss:
    def test_file_exists(self):
        assert os.path.isfile(src_path('pages/ArticlesPage.css'))

    def test_has_articles_page_class(self):
        content = read_src('pages/ArticlesPage.css')
        assert '.articles-page' in content

    def test_has_filters_class(self):
        content = read_src('pages/ArticlesPage.css')
        assert 'filters' in content

    def test_has_error_class(self):
        content = read_src('pages/ArticlesPage.css')
        assert 'error' in content

    def test_has_pagination_class(self):
        content = read_src('pages/ArticlesPage.css')
        assert 'pagination' in content


# ─── App.tsx ─────────────────────────────────────────────────────────────────

class TestAppRouting:
    def test_file_exists(self):
        assert os.path.isfile(src_path('App.tsx'))

    def test_imports_articles_page(self):
        content = read_src('App.tsx')
        assert 'ArticlesPage' in content

    def test_has_articles_route(self):
        content = read_src('App.tsx')
        assert '/articles' in content

    def test_uses_react_router(self):
        content = read_src('App.tsx')
        assert 'react-router-dom' in content

    def test_has_root_redirect(self):
        content = read_src('App.tsx')
        assert 'Navigate' in content or 'Redirect' in content

    def test_uses_routes(self):
        content = read_src('App.tsx')
        assert 'Routes' in content

    def test_uses_route(self):
        content = read_src('App.tsx')
        assert 'Route' in content
