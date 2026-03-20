import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getArticle, updateArticle } from "../api/articles";
import ArticleForm from "../components/ArticleForm";
import { Article, ArticleCreate, ArticleUpdate } from "../types";

/**
 * Extracts a human-readable error message from a FastAPI error response.
 *
 * Handles both `detail: string` and `detail: [{msg: string}]` formats.
 *
 * @param error - The caught error object from an axios request.
 * @returns A string error message.
 */
function extractErrorMessage(error: unknown): string {
  if (
    error !== null &&
    typeof error === "object" &&
    "response" in error
  ) {
    const axiosError = error as { response?: { data?: { detail?: unknown } } };
    const detail = axiosError.response?.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0];
      if (typeof first === "object" && first !== null && "msg" in first) {
        return String((first as { msg: unknown }).msg);
      }
    }
  }

  return "An unexpected error occurred. Please try again.";
}

/**
 * Page for editing an existing article.
 *
 * Fetches the article by ID from the URL params, pre-populates the form,
 * handles submission via updateArticle, and redirects to the detail page
 * on success.
 */
export default function ArticleEditPage(): React.ReactElement {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadError, setLoadError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [serverError, setServerError] = useState<string>("");

  useEffect(() => {
    if (!id) return;

    let cancelled = false;
    setLoading(true);
    setLoadError("");

    getArticle(Number(id))
      .then((data) => {
        if (!cancelled) {
          setArticle(data);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setLoadError("Failed to load article. It may not exist.");
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

  /**
   * Handles form submission for article update.
   *
   * @param data - The article creation payload from the form (used as update payload).
   */
  async function handleSubmit(data: ArticleCreate): Promise<void> {
    if (!id) return;

    setIsSubmitting(true);
    setServerError("");

    const updateData: ArticleUpdate = {
      title: data.title,
      content: data.content,
      status: data.status,
      category_ids: data.category_ids,
    };

    try {
      await updateArticle(Number(id), updateData);
      navigate(`/articles/${id}`);
    } catch (error: unknown) {
      setServerError(extractErrorMessage(error));
    } finally {
      setIsSubmitting(false);
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

  if (loadError) {
    return (
      <main>
        <p role="alert" style={{ color: "red" }}>
          {loadError}
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

  const initialData: Partial<ArticleCreate> = {
    title: article.title,
    content: article.content ?? "",
    status: article.status,
    category_ids: article.categories?.map((c) => c.id) ?? article.category_ids ?? [],
  };

  return (
    <main>
      <h1>Edit Article</h1>
      <ArticleForm
        initialData={initialData}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        serverError={serverError}
      />
    </main>
  );
}
