import client from "./client";
import { Article, ArticleCreate, ArticleListParams, ArticleListResponse, ArticleUpdate } from "../types";

/**
 * Fetches a paginated list of articles with optional filters.
 *
 * @param params - Optional query parameters for filtering/pagination.
 * @returns Promise resolving to an ArticleListResponse.
 */
export async function getArticles(params?: ArticleListParams): Promise<ArticleListResponse> {
  const response = await client.get<ArticleListResponse>("/articles", { params });
  return response.data;
}

/**
 * Fetches a single article by its ID.
 *
 * @param id - The numeric ID of the article.
 * @returns Promise resolving to an Article object.
 */
export async function getArticle(id: number): Promise<Article> {
  const response = await client.get<Article>(`/articles/${id}`);
  return response.data;
}

/**
 * Creates a new article.
 *
 * @param data - The article creation payload.
 * @returns Promise resolving to the created Article object.
 */
export async function createArticle(data: ArticleCreate): Promise<Article> {
  const response = await client.post<Article>("/articles", data);
  return response.data;
}

/**
 * Updates an existing article by its ID.
 *
 * @param id - The numeric ID of the article to update.
 * @param data - The article update payload (all fields optional).
 * @returns Promise resolving to the updated Article object.
 */
export async function updateArticle(id: number, data: ArticleUpdate): Promise<Article> {
  const response = await client.put<Article>(`/articles/${id}`, data);
  return response.data;
}

/**
 * Deletes an article by its ID.
 *
 * @param id - The numeric ID of the article to delete.
 * @returns Promise resolving to void on success (204 No Content).
 */
export async function deleteArticle(id: number): Promise<void> {
  await client.delete(`/articles/${id}`);
}
