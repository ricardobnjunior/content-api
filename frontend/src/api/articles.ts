/**
 * API functions for article-related operations.
 */
import apiClient from "./client";
import type { Article, CreateArticlePayload, UpdateArticlePayload, ImageResponse } from "../types";

/**
 * Fetches a paginated list of articles.
 * @returns Promise resolving to an array of Article objects.
 */
export async function getArticles(): Promise<Article[]> {
  const response = await apiClient.get<Article[]>("/api/v1/articles");
  return response.data;
}

/**
 * Fetches a single article by ID.
 * @param id - The article ID.
 * @returns Promise resolving to an Article object.
 */
export async function getArticle(id: number): Promise<Article> {
  const response = await apiClient.get<Article>(`/api/v1/articles/${id}`);
  return response.data;
}

/**
 * Creates a new article.
 * @param payload - The article creation payload.
 * @returns Promise resolving to the created Article object.
 */
export async function createArticle(payload: CreateArticlePayload): Promise<Article> {
  const response = await apiClient.post<Article>("/api/v1/articles", payload);
  return response.data;
}

/**
 * Updates an existing article.
 * @param id - The article ID to update.
 * @param payload - The article update payload.
 * @returns Promise resolving to the updated Article object.
 */
export async function updateArticle(id: number, payload: UpdateArticlePayload): Promise<Article> {
  const response = await apiClient.put<Article>(`/api/v1/articles/${id}`, payload);
  return response.data;
}

/**
 * Deletes an article by ID.
 * @param id - The article ID to delete.
 * @returns Promise resolving to void.
 */
export async function deleteArticle(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/articles/${id}`);
}

/**
 * Uploads an image for a specific article.
 * Sends the file as multipart/form-data with the field name "file".
 * @param articleId - The article ID to associate the image with.
 * @param file - The image File object to upload.
 * @returns Promise resolving to an ImageResponse with filename, url, and size.
 */
export async function uploadArticleImage(articleId: number, file: File): Promise<ImageResponse> {
  const fd = new FormData();
  fd.append("file", file);
  const response = await apiClient.post<ImageResponse>(
    `/api/v1/articles/${articleId}/image`,
    fd,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return response.data;
}

/**
 * Deletes the image associated with a specific article.
 * @param articleId - The article ID whose image should be deleted.
 * @returns Promise resolving to void.
 */
export async function deleteArticleImage(articleId: number): Promise<void> {
  await apiClient.delete(`/api/v1/articles/${articleId}/image`);
}
