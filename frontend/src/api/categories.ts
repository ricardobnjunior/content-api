import client from "./client";
import { Category } from "../types";

/**
 * Fetches all available categories from the API.
 *
 * @returns Promise resolving to an array of Category objects.
 */
export async function getCategories(): Promise<Category[]> {
  const response = await client.get<Category[]>("/categories");
  return response.data;
}
