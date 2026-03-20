import axios from "axios";

/**
 * Configured Axios instance for API requests.
 *
 * Uses a base URL of `/api/v1` so all requests are relative to
 * the backend API prefix. In development this is proxied by Vite.
 */
const client = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

export default client;
