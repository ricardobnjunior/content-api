import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { deleteArticle, getArticle } from "../api/articles";
import { Article } from "../types";

/**
 * Read-only detail view for a single article.
 *
 * Fetches the article by ID from the URL params, displays all fields,
 * and provides Edit and Delete actions.
 */
export default function ArticleDetailPage(): React.ReactElement {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  useEffect(() => {
    if (!id) return;

    let cancelled = false;
    setLoading(true);
    setError("");

    getArticle(Number(id))
      .then((data) => {
        if (!cancelled) {
          setArticle(data);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError("Article not found or could not be loaded.");
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
  }, [id]);

  /** Navigates to the edit page for this article. */
  function handleEdit(): void {
    navigate(`/articles/${id}/edit`);
  }

  /**
   * Prompts the user to confirm deletion, then deletes the article
   * and redirects to the articles list on success.
   */
  async function handleDelete(): Promise<void> {
    if (!id) return;

    const confirmed = window.confirm(
      "Are you sure you want to delete this article? This action cannot be undone."
    );

    if (!confirmed) return;

    setIsDeleting(true);

    try {
      await deleteArticle(Number(id));
      navigate("/articles");
    } catch {
      setError("Failed to delete the article. Please try again.");
      setIsDeleting(false);
    }
  }

  if (loading) {
    return (
      <main>
        <p aria-live="polite" aria-busy="true">
          Loading article…
        </p>
      </main>
    );
  }

  if (error) {
    return (
      <main>
        <p role="alert" style={{ color: "red" }}>
          {error}
        </p>
        <button type="button" onClick={() => navigate("/articles")}>
          Back to Articles
        </button>
      </main>
    );
  }

  if (!article) {
    return (
      <main>
        <p>Article not found.</p>
        <button type="button" onClick={() => navigate("/articles")}>
          Back to Articles
        </button>
      </main>
    );
  }

  return (
    <main>
      <article aria-label={`Article: ${article.title}`}>
        <header>
          <h1>{article.title}</h1>
          <p>
            <strong>Status:</strong>{" "}
            <span
              aria-label={`Status: ${article.status}`}
              style={{
                textTransform: "capitalize",
                color: article.status === "published" ? "green" : "gray",
              }}
            >
              {article.status}
            </span>
          </p>

          {article.categories && article.categories.length > 0 && (
            <section aria-label="Categories">
              <strong>Categories:</strong>{" "}
              <ul
                style={{ display: "inline-flex", gap: "0.5rem", listStyle: "none", padding: 0 }}
              >
                {article.categories.map((category) => (
                  <li key={category.id}>
                    <span>{category.name}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {article.created_at && (
            <p>
              <strong>Created:</strong>{" "}
              <time dateTime={article.created_at}>
                {new Date(article.created_at).toLocaleDateString()}
              </time>
            </p>
          )}

          {article.updated_at && (
            <p>
              <strong>Last updated:</strong>{" "}
              <time dateTime={article.updated_at}>
                {new Date(article.updated_at).toLocaleDateString()}
              </time>
            </p>
          )}
        </header>

        {article.content ? (
          <section aria-label="Article content">
            <h2>Content</h2>
            <p style={{ whiteSpace: "pre-wrap" }}>{article.content}</p>
          </section>
        ) : (
          <section aria-label="Article content">
            <p style={{ color: "gray", fontStyle: "italic" }}>No content provided.</p>
          </section>
        )}
      </article>

      <nav aria-label="Article actions" style={{ marginTop: "2rem", display: "flex", gap: "1rem" }}>
        <button
          type="button"
          onClick={handleEdit}
          aria-label="Edit this article"
          disabled={isDeleting}
        >
          Edit
        </button>
        <button
          type="button"
          onClick={handleDelete}
          disabled={isDeleting}
          aria-label="Delete this article"
          aria-busy={isDeleting}
          style={{ color: "red" }}
        >
          {isDeleting ? "Deleting…" : "Delete"}
        </button>
        <button
          type="button"
          onClick={() => navigate("/articles")}
          aria-label="Back to articles list"
        >
          Back to Articles
        </button>
      </nav>
    </main>
  );
}
