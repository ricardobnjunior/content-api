import React from 'react';
import { Link } from 'react-router-dom';
import { Article } from '../types/index';

/**
 * Props for the ArticleTable component.
 */
interface ArticleTableProps {
  /** List of articles to display */
  articles: Article[];
  /** Whether the data is currently loading */
  loading: boolean;
}

const statusColors: Record<string, React.CSSProperties> = {
  published: {
    backgroundColor: '#d1fae5',
    color: '#065f46',
  },
  draft: {
    backgroundColor: '#fef3c7',
    color: '#92400e',
  },
};

const badgeStyle = (status: string): React.CSSProperties => ({
  display: 'inline-block',
  padding: '2px 10px',
  borderRadius: '12px',
  fontSize: '12px',
  fontWeight: 600,
  textTransform: 'capitalize',
  ...(statusColors[status] ?? { backgroundColor: '#e5e7eb', color: '#374151' }),
});

/**
 * Table component for displaying a list of articles.
 * Handles loading and empty states with appropriate messages.
 *
 * @param props - ArticleTable props
 */
const ArticleTable: React.FC<ArticleTableProps> = ({ articles, loading }) => {
  const renderBody = () => {
    if (loading) {
      return (
        <tr>
          <td
            colSpan={4}
            style={{ textAlign: 'center', padding: '32px', color: '#6b7280' }}
            aria-live="polite"
            aria-busy="true"
          >
            Loading articles...
          </td>
        </tr>
      );
    }

    if (articles.length === 0) {
      return (
        <tr>
          <td
            colSpan={4}
            style={{ textAlign: 'center', padding: '32px', color: '#6b7280' }}
            aria-live="polite"
          >
            No articles found.
          </td>
        </tr>
      );
    }

    return articles.map((article) => (
      <tr
        key={article.id}
        style={{ borderBottom: '1px solid #e5e7eb' }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLTableRowElement).style.backgroundColor = '#f9fafb';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLTableRowElement).style.backgroundColor = '';
        }}
      >
        <td style={{ padding: '14px 16px', fontSize: '14px', color: '#111827', fontWeight: 500 }}>
          {article.title}
        </td>
        <td style={{ padding: '14px 16px' }}>
          <span style={badgeStyle(article.status)}>{article.status}</span>
        </td>
        <td style={{ padding: '14px 16px', fontSize: '14px', color: '#6b7280' }}>
          {new Date(article.created_at).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
          })}
        </td>
        <td style={{ padding: '14px 16px' }}>
          <Link
            to={`/articles/${article.id}`}
            style={{
              color: '#3b82f6',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: 500,
            }}
            aria-label={`View article: ${article.title}`}
          >
            View
          </Link>
        </td>
      </tr>
    ));
  };

  return (
    <div style={{ overflowX: 'auto', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
      <table
        style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: '#fff' }}
        aria-label="Articles list"
        role="table"
      >
        <thead>
          <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
            <th
              scope="col"
              style={{ padding: '12px 16px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: '#374151', textTransform: 'uppercase', letterSpacing: '0.05em' }}
            >
              Title
            </th>
            <th
              scope="col"
              style={{ padding: '12px 16px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: '#374151', textTransform: 'uppercase', letterSpacing: '0.05em' }}
            >
              Status
            </th>
            <th
              scope="col"
              style={{ padding: '12px 16px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: '#374151', textTransform: 'uppercase', letterSpacing: '0.05em' }}
            >
              Created At
            </th>
            <th
              scope="col"
              style={{ padding: '12px 16px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: '#374151', textTransform: 'uppercase', letterSpacing: '0.05em' }}
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody>{renderBody()}</tbody>
      </table>
    </div>
  );
};

export default ArticleTable;
