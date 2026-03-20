/**
 * TypeScript interfaces matching the backend API schemas.
 */

/** Represents a news article from the backend. */
export interface Article {
  id: number;
  title: string;
  content: string | null;
  status: string;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

/** Pagination metadata returned with list responses. */
export interface PaginationMeta {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

/** Paginated list of articles. */
export interface ArticleList {
  items: Article[];
  meta: PaginationMeta;
}

/** Represents a content category. */
export interface Category {
  id: number;
  name: string;
}
