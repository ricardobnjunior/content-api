import axios, { AxiosError } from "axios";

/**
 * Configured Axios instance for all API requests.
 * Base URL is set to /api/v1, which Vite proxies to the FastAPI backend.
 */
const apiClient = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Response error interceptor — logs the error and re-throws it
 * so callers can handle it appropriately.
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error(
      "[API Error]",
      error.response?.status,
      error.response?.data ?? error.message
    );
    return Promise.reject(error);
  }
);

export default apiClient;
