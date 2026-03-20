import React from 'react';

/**
 * Props for the Pagination component.
 */
interface PaginationProps {
  /** Current active page number (1-based) */
  currentPage: number;
  /** Total number of pages */
  totalPages: number;
  /** Callback invoked when the user navigates to a new page */
  onPageChange: (page: number) => void;
}

const buttonStyle: React.CSSProperties = {
  padding: '8px 16px',
  border: '1px solid #d1d5db',
  borderRadius: '6px',
  backgroundColor: '#fff',
  cursor: 'pointer',
  fontSize: '14px',
  fontWeight: 500,
  color: '#374151',
  transition: 'background-color 0.15s, border-color 0.15s',
};

const disabledButtonStyle: React.CSSProperties = {
  ...buttonStyle,
  opacity: 0.4,
  cursor: 'not-allowed',
};

/**
 * Reusable pagination controls with Previous/Next buttons and a page indicator.
 * Always renders to maintain consistent layout, disabling buttons at boundaries.
 *
 * @param props - Pagination props
 */
const Pagination: React.FC<PaginationProps> = ({ currentPage, totalPages, onPageChange }) => {
  const isFirstPage = currentPage <= 1;
  const isLastPage = currentPage >= totalPages || totalPages === 0;

  const handlePrevious = () => {
    if (!isFirstPage) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (!isLastPage) {
      onPageChange(currentPage + 1);
    }
  };

  return (
    <nav
      aria-label="Pagination navigation"
      role="navigation"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        justifyContent: 'center',
        padding: '16px 0',
      }}
    >
      <button
        onClick={handlePrevious}
        disabled={isFirstPage}
        aria-label="Go to previous page"
        aria-disabled={isFirstPage}
        style={isFirstPage ? disabledButtonStyle : buttonStyle}
        onMouseEnter={(e) => {
          if (!isFirstPage) {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#f3f4f6';
          }
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#fff';
        }}
      >
        ← Previous
      </button>

      <span
        aria-live="polite"
        aria-atomic="true"
        style={{ fontSize: '14px', color: '#6b7280', fontWeight: 500, minWidth: '100px', textAlign: 'center' }}
      >
        {totalPages === 0 ? 'No pages' : `Page ${currentPage} of ${totalPages}`}
      </span>

      <button
        onClick={handleNext}
        disabled={isLastPage}
        aria-label="Go to next page"
        aria-disabled={isLastPage}
        style={isLastPage ? disabledButtonStyle : buttonStyle}
        onMouseEnter={(e) => {
          if (!isLastPage) {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#f3f4f6';
          }
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#fff';
        }}
      >
        Next →
      </button>
    </nav>
  );
};

export default Pagination;
