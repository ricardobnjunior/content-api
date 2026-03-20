import React from 'react';
import { Category } from '../types/index';

/** Props for the CategoryList component. */
interface CategoryListProps {
  /** Array of categories to display. */
  categories: Category[];
}

/**
 * Presentational component that renders a table of categories.
 * Shows an empty-state message when there are no categories.
 *
 * @param props - Component props containing the categories array.
 * @returns A table of categories or an empty-state message.
 */
const CategoryList: React.FC<CategoryListProps> = ({ categories }) => {
  if (categories.length === 0) {
    return <p role="status">No categories yet</p>;
  }

  return (
    <table aria-label="Categories list">
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col">Articles</th>
        </tr>
      </thead>
      <tbody>
        {categories.map((category) => (
          <tr key={category.id}>
            <td>{category.name}</td>
            <td>{(category as Category & { articleCount?: number }).articleCount ?? '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default CategoryList;
