import client from './client';
import { Category } from '../types/index';

/**
 * Fetches all categories from the API.
 * @returns Promise resolving to an array of Category objects.
 */
export async function getCategories(): Promise<Category[]> {
  const response = await client.get<Category[]>('/api/v1/categories');
  return response.data;
}

/**
 * Creates a new category.
 * @param data - Object containing the category name.
 * @returns Promise resolving to the created Category object.
 */
export async function createCategory(data: { name: string }): Promise<Category> {
  const response = await client.post<Category>('/api/v1/categories', { name: data.name });
  return response.data;
}
