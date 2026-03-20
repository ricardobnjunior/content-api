import React, { useEffect, useState } from "react";
import { getCategories } from "../api/categories";
import { ArticleCreate, Category } from "../types";

/** Props for the ArticleForm component. */
export interface ArticleFormProps {
  /** Pre-populated data for edit mode; omit for create mode. */
  initialData?: Partial<ArticleCreate>;
  /** Async callback invoked on form submission with collected data. */
  onSubmit: (data: ArticleCreate) => Promise<void>;
  /** Whether the form is currently submitting (disables inputs). */
  isSubmitting?: boolean;
  /** Server-side error message to display below the form. */
  serverError?: string;
}

/**
 * Reusable controlled form for creating and editing articles.
 *
 * Loads categories from the API on mount. Supports pre-population
 * via `initialData` for edit scenarios.
 */
export default function ArticleForm({
  initialData,
  onSubmit,
  isSubmitting = false,
  serverError,
}: ArticleFormProps): React.ReactElement {
  const [title, setTitle] = useState<string>(initialData?.title ?? "");
  const [content, setContent] = useState<string>(initialData?.content ?? "");
  const [status, setStatus] = useState<"draft" | "published">(
    initialData?.status ?? "draft"
  );
  const [selectedCategoryIds, setSelectedCategoryIds] = useState<number[]>(
    initialData?.category_ids ?? []
  );
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState<boolean>(true);
  const [categoriesError, setCategoriesError] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    getCategories()
      .then((data) => {
        if (!cancelled) {
          setCategories(data);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setCategoriesError("Failed to load categories.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setCategoriesLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Sync initialData changes (e.g., when edit page finishes loading)
  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title ?? "");
      setContent(initialData.content ?? "");
      setStatus(initialData.status ?? "draft");
      setSelectedCategoryIds(initialData.category_ids ?? []);
    }
  }, [initialData?.title, initialData?.content, initialData?.status]);

  /**
   * Handles checkbox state changes for category selection.
   *
   * @param categoryId - The ID of the toggled category.
   * @param checked - Whether the checkbox was checked or unchecked.
   */
  function handleCategoryChange(categoryId: number, checked: boolean): void {
    setSelectedCategoryIds((prev) =>
      checked ? [...prev, categoryId] : prev.filter((id) => id !== categoryId)
    );
  }

  /**
   * Handles form submission by preventing default browser behavior
   * and calling the provided onSubmit callback.
   *
   * @param event - The form submit event.
   */
  async function handleSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();

    const formData: ArticleCreate = {
      title,
      content: content || undefined,
      status,
      category_ids: selectedCategoryIds.length > 0 ? selectedCategoryIds : undefined,
    };

    await onSubmit(formData);
  }

  return (
    <form onSubmit={handleSubmit} noValidate aria-label="Article form">
      {/* Title */}
      <div className="form-group">
        <label htmlFor="article-title">
          Title <span aria-hidden="true">*</span>
        </label>
        <input
          id="article-title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          disabled={isSubmitting}
          aria-required="true"
          aria-label="Article title"
          placeholder="Enter article title"
        />
      </div>

      {/* Content */}
      <div className="form-group">
        <label htmlFor="article-content">Content</label>
        <textarea
          id="article-content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          disabled={isSubmitting}
          aria-label="Article content"
          placeholder="Enter article content"
          rows={10}
        />
      </div>

      {/* Status */}
      <div className="form-group">
        <label htmlFor="article-status">Status</label>
        <select
          id="article-status"
          value={status}
          onChange={(e) => setStatus(e.target.value as "draft" | "published")}
          disabled={isSubmitting}
          aria-label="Article status"
        >
          <option value="draft">Draft</option>
          <option value="published">Published</option>
        </select>
      </div>

      {/* Categories */}
      <div className="form-group">
        <fieldset>
          <legend>Categories</legend>
          {categoriesLoading && (
            <p aria-live="polite" aria-busy="true">
              Loading categories…
            </p>
          )}
          {categoriesError && (
            <p role="alert" style={{ color: "red" }}>
              {categoriesError}
            </p>
          )}
          {!categoriesLoading && !categoriesError && categories.length === 0 && (
            <p>No categories available.</p>
          )}
          {!categoriesLoading &&
            categories.map((category) => (
              <label key={category.id} className="category-label">
                <input
                  type="checkbox"
                  value={category.id}
                  checked={selectedCategoryIds.includes(category.id)}
                  onChange={(e) =>
                    handleCategoryChange(category.id, e.target.checked)
                  }
                  disabled={isSubmitting}
                  aria-label={`Category: ${category.name}`}
                />
                {" "}{category.name}
              </label>
            ))}
        </fieldset>
      </div>

      {/* Server error */}
      {serverError && (
        <div role="alert" aria-live="assertive" style={{ color: "red", marginBottom: "1rem" }}>
          <strong>Error:</strong> {serverError}
        </div>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={isSubmitting || !title.trim()}
        aria-disabled={isSubmitting || !title.trim()}
      >
        {isSubmitting ? "Saving…" : "Save Article"}
      </button>
    </form>
  );
}
