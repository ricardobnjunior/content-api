/**
 * Core TypeScript interfaces for the application.
 */

/** Represents an article entity. */
export interface Article {
  id: number;
  title: string;
  body: string;
  created_at: string;
  updated_at: string;
  image_url?: string | null;
}

/** Payload for creating a new article. */
export interface CreateArticlePayload {
  title: string;
  body: string;
}

/** Payload for updating an existing article. */
export interface UpdateArticlePayload {
  title?: string;
  body?: string;
}

/** Response returned after uploading an image. */
export interface ImageResponse {
  filename: string;
  url: string;
  size: number;
}
