/**
 * ArticleDetailPage — displays a single article with edit, delete, and image management options.
 */
import React, { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { deleteArticle, deleteArticleImage, getArticle } from "../api/articles";
import ImageUpload from "../components/ImageUpload";
import type { Article } from "../types";

/**
 * Page component that fetches and displays a single article by ID.
 * Provides options to edit, delete the article, and upload/delete its image.
 *
 * @returns The ArticleDetailPage component.
 */
const ArticleDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetches the article data from the backend.
   */
  const fetchArticle = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getArticle(Number(id));
      setArticle(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to load article.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchArticle();
  }, [fetchArticle]);

  /**
   * Handles article deletion with a confirmation dialog.
   * Navigates to the articles list on success.
   */
  const handleDeleteArticle = async () => {
    if (!article) return;
    const confirmed = window.confirm(
      `Are you sure you want to delete "${article.title}"?`
    );
    if (!confirmed) return;

    try {
      await deleteArticle(article.id);
      navigate("/articles");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to delete article.";
      setError(message);
    }
  };

  /**
   * Handles image deletion with a confirmation dialog.
   * Refreshes the article after deletion.
   */
  const handleDeleteImage = async () => {
    if (!article) return;
    const confirmed = window.confirm(
      "Are you sure you want to delete the image for this article?"
    );
    if (!confirmed) return;

    try {
      await deleteArticleImage(article.id);
      await fetchArticle();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to delete image.";
      setError(message);
    }
  };

  if (loading) {
    return (
      <main>
        <p aria-live="polite">Loading article…</p>
      </main>
    );
  }

  if (error) {
    return (
      <main>
        <p role="alert" style={{ color: "red" }}>
          {error}
        </p>
        <Link to="/articles">Back to articles</Link>
      </main>
    );
  }

  if (!article) {
    return (
      <main>
        <p>Article not found.</p>
        <Link to="/articles">Back to articles</Link>
      </main>
    );
  }

  return (
    <main>
      <nav aria-label="Breadcrumb">
        <Link to="/articles">← Back to articles</Link>
      </nav>

      <article>
        <h1>{article.title}</h1>
        <p>{article.body}</p>

        <section aria-label="Article image">
          <h2>Image</h2>
          {article.image_url ? (
            <div>
              <img
                src={article.image_url}
                alt="Article image"
                style={{ maxWidth: "100%", maxHeight: "400px", display: "block", marginBottom: "0.5rem" }}
              />
              <button
                type="button"
                onClick={handleDeleteImage}
                aria-label="Delete article image"
              >
                Delete Image
              </button>
            </div>
          ) : (
            <div>
              <p>No image</p>
              <ImageUpload articleId={article.id} onUploadSuccess={fetchArticle} />
            </div>
          )}
        </section>

        <section aria-label="Article actions" style={{ marginTop: "1rem" }}>
          <Link to={`/articles/${article.id}/edit`}>
            <button type="button" aria-label={`Edit article: ${article.title}`}>
              Edit
            </button>
          </Link>
          <button
            type="button"
            onClick={handleDeleteArticle}
            aria-label={`Delete article: ${article.title}`}
            style={{ marginLeft: "0.5rem" }}
          >
            Delete
          </button>
        </section>
      </article>
    </main>
  );
};

export default ArticleDetailPage;
