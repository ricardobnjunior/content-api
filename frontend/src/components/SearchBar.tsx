import React, { useEffect, useRef, useState } from 'react';

/**
 * Props for the SearchBar component.
 */
interface SearchBarProps {
  /** Current search value (controlled by parent after debounce) */
  value: string;
  /** Callback invoked with the debounced search value */
  onChange: (value: string) => void;
  /** Placeholder text for the input */
  placeholder?: string;
}

/**
 * Search input component with 300ms debounce.
 * Manages its own display state for responsive UI while debouncing the onChange callback.
 *
 * @param props - SearchBar props
 */
const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  placeholder = 'Search articles...',
}) => {
  const [displayValue, setDisplayValue] = useState(value);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync display value when parent resets value externally
  useEffect(() => {
    setDisplayValue(value);
  }, [value]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current !== null) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setDisplayValue(newValue);

    if (timerRef.current !== null) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(() => {
      onChange(newValue);
    }, 300);
  };

  return (
    <div className="search-bar" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <label htmlFor="article-search" style={{ fontWeight: 500, whiteSpace: 'nowrap' }}>
        Search:
      </label>
      <input
        id="article-search"
        type="text"
        value={displayValue}
        onChange={handleChange}
        placeholder={placeholder}
        aria-label="Search articles"
        style={{
          padding: '8px 12px',
          border: '1px solid #d1d5db',
          borderRadius: '6px',
          fontSize: '14px',
          width: '240px',
          outline: 'none',
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = '#3b82f6';
          e.currentTarget.style.boxShadow = '0 0 0 2px rgba(59,130,246,0.2)';
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = '#d1d5db';
          e.currentTarget.style.boxShadow = 'none';
        }}
      />
    </div>
  );
};

export default SearchBar;
