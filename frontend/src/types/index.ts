/**
 * Core type definitions for the frontend application.
 */

/** Represents a category associated with articles. */
export interface Category {
  id: number;
  name: string;
  slug: string;
}

/** Represents an article returned from the API. */
export interface Article {
  id: number;
  title: string;
  content?: string;
  status: "draft" | "published";
  category_ids?: number[];
  categories: Category[];
  created_at?: string;
  updated_at?: string;
}

/** Payload for creating a new article. */
export interface ArticleCreate {
  title: string;
  content?: string;
  status?: "draft" | "published";
  category_ids?: number[];
}

/** Payload for updating an existing article. */
export interface ArticleUpdate {
  title?: string;
  content?: string;
  status?: "draft" | "published";
  category_ids?: number[];
}

/** Query parameters for listing articles. */
export interface ArticleListParams {
  skip?: number;
  limit?: number;
  status?: "draft" | "published";
  category_id?: number;
}

/** Paginated list response for articles. */
export interface ArticleListResponse {
  items: Article[];
  total: number;
  skip: number;
  limit: number;
}
