import React, { useEffect, useState } from 'react';
import { Category } from '../types/index';
import { getCategories, createCategory } from '../api/categories';
import CategoryList from '../components/CategoryList';

/**
 * Page component for managing categories.
 * Displays an inline form for creating categories and a list of existing ones.
 *
 * @returns The categories management page.
 */
const CategoriesPage: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [newName, setNewName] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  useEffect(() => {
    let cancelled = false;

    const fetchCategories = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getCategories();
        if (!cancelled) {
          setCategories(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError('Failed to load categories. Please try again.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchCategories();

    return () => {
      cancelled = true;
    };
  }, []);

  /**
   * Handles form submission to create a new category.
   * Validates input, calls the API, and prepends the result to the list.
   *
   * @param event - The form submit event.
   */
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedName = newName.trim();
    if (!trimmedName) {
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const created = await createCategory({ name: trimmedName });
      setCategories((prev) => [created, ...prev]);
      setNewName('');
    } catch (err) {
      setError('Failed to create category. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main>
      <h1>Categories</h1>

      <section aria-label="Create new category">
        <form onSubmit={handleSubmit} noValidate>
          <label htmlFor="category-name-input">New category name</label>
          <input
            id="category-name-input"
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Enter category name"
            disabled={submitting}
            aria-required="true"
          />
          <button
            type="submit"
            disabled={submitting || newName.trim() === ''}
            aria-busy={submitting}
          >
            {submitting ? 'Adding…' : 'Add'}
          </button>
        </form>
      </section>

      {error && (
        <p role="alert" style={{ color: 'red' }}>
          {error}
        </p>
      )}

      {loading ? (
        <p role="status" aria-live="polite">
          Loading categories…
        </p>
      ) : (
        <section aria-label="Categories list">
          <CategoryList categories={categories} />
        </section>
      )}
    </main>
  );
};

export default CategoriesPage;
