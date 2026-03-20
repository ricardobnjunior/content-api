import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createArticle } from "../api/articles";
import ArticleForm from "../components/ArticleForm";
import { ArticleCreate } from "../types";

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
 * Page for creating a new article.
 *
 * Renders an empty ArticleForm and handles submission by calling
 * the createArticle API, then redirects to the new article's detail page.
 */
export default function ArticleCreatePage(): React.ReactElement {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [serverError, setServerError] = useState<string>("");

  /**
   * Handles form submission for article creation.
   *
   * @param data - The article creation payload from the form.
   */
  async function handleSubmit(data: ArticleCreate): Promise<void> {
    setIsSubmitting(true);
    setServerError("");

    try {
      const article = await createArticle(data);
      navigate(`/articles/${article.id}`);
    } catch (error: unknown) {
      setServerError(extractErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main>
      <h1>Create New Article</h1>
      <ArticleForm
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        serverError={serverError}
      />
    </main>
  );
}
