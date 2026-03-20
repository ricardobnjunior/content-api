import React, { useEffect, useState } from 'react';
import { getArticles } from '../api/articles';
import ArticleTable from '../components/ArticleTable';
import Layout from '../components/Layout';
import Pagination from '../components/Pagination';
import SearchBar from '../components/SearchBar';
import { Article, PaginationMeta } from '../types/index';
import './ArticlesPage.css';

/**
 * Articles listing page.
 *
 * Displays a searchable, filterable, paginated table of articles.
 * Manages all state locally and composes ArticleTable, SearchBar, and Pagination.
 */
const ArticlesPage: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [meta, setMeta] = useState<PaginationMeta | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination state
  const [page, setPage] = useState<number>(1);

  // Filter state
  const [status, setStatus] = useState<string>('');

  // Search state: searchInput is what the user types; search is the debounced value
  const [searchInput, setSearchInput] = useState<string>('');
  const [search, setSearch] = useState<string>('');

  // Debounce searchInput → search, reset page on change
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
      setPage(1);
    }, 300);

    return () => {
      clearTimeout(timer);
    };
  }, [searchInput]);

  // Fetch articles when page, status, or debounced search changes
  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;

    const fetchArticles = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getArticles({
          page,
          per_page: 10,
          status: status || undefined,
          search: search || undefined,
        });

        if (!cancelled) {
          setArticles(data.items);
          setMeta(data.meta);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          // AbortError is expected on cleanup — don't show error for it
          if (err instanceof Error && err.name === 'AbortError') {
            return;
          }
          // Axios cancellation
          if (
            err instanceof Error &&
            err.message &&
            err.message.toLowerCase().includes('cancel')
          ) {
            return;
          }
          setError('Failed to load articles. Please try again.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchArticles();

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [page, status, search]);

  /**
   * Handle status filter change.
   * Resets page to 1 when filter changes.
   */
  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStatus(e.target.value);
    setPage(1);
  };

  /**
   * Handle search input change from SearchBar.
   * SearchBar calls this after its own internal debounce,
   * but ArticlesPage also debounces via useEffect to be safe.
   */
  const handleSearchChange = (value: string) => {
    setSearchInput(value);
  };

  const totalPages = meta?.total_pages ?? 0;

  return (
    <Layout>
      <main className="articles-page" aria-labelledby="articles-title">
        <header className="articles-page__header">
          <h1 id="articles-title" className="articles-page__title">
            Articles
          </h1>
          <p className="articles-page__subtitle">
            Browse and manage all articles
          </p>
        </header>

        {/* Filters: search and status */}
        <section
          className="articles-page__filters"
          aria-label="Article filters"
        >
          <SearchBar
            value={searchInput}
            onChange={handleSearchChange}
            placeholder="Search articles..."
          />

          <div className="articles-page__status-filter">
            <label
              htmlFor="status-filter"
              className="articles-page__status-label"
            >
              Status:
            </label>
            <select
              id="status-filter"
              value={status}
              onChange={handleStatusChange}
              className="articles-page__status-select"
              aria-label="Filter by status"
            >
              <option value="">All</option>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
            </select>
          </div>
        </section>

        {/* Error message */}
        {error !== null && (
          <div
            className="articles-page__error"
            role="alert"
            aria-live="assertive"
          >
            {error}
          </div>
        )}

        {/* Articles table */}
        <ArticleTable articles={articles} loading={loading} />

        {/* Pagination controls */}
        {!loading && (
          <div className="articles-page__pagination">
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={setPage}
            />
          </div>
        )}
      </main>
    </Layout>
  );
};

export default ArticlesPage;
