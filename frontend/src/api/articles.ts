import { ArticleList } from '../types/index';
import client from './client';

/**
 * Parameters for fetching articles list.
 */
export interface GetArticlesParams {
  page?: number;
  per_page?: number;
  status?: string;
  search?: string;
  category_id?: number;
}

/**
 * Fetch a paginated list of articles from the API.
 *
 * @param params - Optional query parameters for filtering and pagination.
 * @returns A promise resolving to an ArticleList with items and pagination meta.
 */
export async function getArticles(params?: GetArticlesParams): Promise<ArticleList> {
  const response = await client.get<ArticleList>('/articles', { params });
  return response.data;
}
