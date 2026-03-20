import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getArticles } from "../api/articles";
import { Article } from "../types";

/**
 * Page displaying a list of all articles.
 *
 * Fetches articles on mount and renders them with links to their
 * detail pages. Includes a button to navigate to the create page.
 */
export default function ArticleListPage(): React.ReactElement {
  const navigate = useNavigate();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    getArticles()
      .then((data) => {
        if (!cancelled) {
          // Handle both paginated response and plain array
          const items = Array.isArray(data) ? data : (data as { items?: Article[] }).items ?? [];
          setArticles(items);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError("Failed to load articles.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Articles</h1>
        <button
          type="button"
          onClick={() => navigate("/articles/new")}
          aria-label="Create new article"
        >
          New Article
        </button>
      </header>

      {loading && (
        <p aria-live="polite" aria-busy="true">
          Loading articles…
        </p>
      )}

      {error && (
        <p role="alert" style={{ color: "red" }}>
          {error}
        </p>
      )}

      {!loading && !error && articles.length === 0 && (
        <p>No articles found. Create your first article!</p>
      )}

      {!loading && !error && articles.length > 0 && (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {articles.map((article) => (
            <li
              key={article.id}
              style={{ marginBottom: "1rem", borderBottom: "1px solid #eee", paddingBottom: "1rem" }}
            >
              <h2 style={{ margin: 0 }}>
                <button
                  type="button"
                  onClick={() => navigate(`/articles/${article.id}`)}
                  aria-label={`View article: ${article.title}`}
                  style={{ background: "none", border: "none", cursor: "pointer", padding: 0, fontSize: "inherit", textDecoration: "underline" }}
                >
                  {article.title}
                </button>
              </h2>
              <p style={{ margin: "0.25rem 0", color: "gray", textTransform: "capitalize" }}>
                {article.status}
              </p>
              {article.categories && article.categories.length > 0 && (
                <p style={{ margin: "0.25rem 0", fontSize: "0.875rem" }}>
                  {article.categories.map((c) => c.name).join(", ")}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
