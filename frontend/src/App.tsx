import React from "react";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import ArticleCreatePage from "./pages/ArticleCreatePage";
import ArticleDetailPage from "./pages/ArticleDetailPage";
import ArticleEditPage from "./pages/ArticleEditPage";
import ArticleListPage from "./pages/ArticleListPage";

/**
 * Root application component with client-side routing.
 *
 * Routes:
 * - `/articles`          → ArticleListPage
 * - `/articles/new`      → ArticleCreatePage (must be before `:id`)
 * - `/articles/:id`      → ArticleDetailPage
 * - `/articles/:id/edit` → ArticleEditPage
 */
export default function App(): React.ReactElement {
  return (
    <Router>
      <Routes>
        <Route path="/articles" element={<ArticleListPage />} />
        <Route path="/articles/new" element={<ArticleCreatePage />} />
        <Route path="/articles/:id" element={<ArticleDetailPage />} />
        <Route path="/articles/:id/edit" element={<ArticleEditPage />} />
        <Route path="*" element={<ArticleListPage />} />
      </Routes>
    </Router>
  );
}
