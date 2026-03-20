import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";

/**
 * Placeholder component for the Articles page.
 * Will be replaced by a full implementation in a subsequent issue.
 */
const ArticlesPage: React.FC = () => (
  <section aria-labelledby="articles-heading">
    <h1 id="articles-heading">Articles</h1>
    <p>Articles list coming soon.</p>
  </section>
);

/**
 * Placeholder component for the Categories page.
 * Will be replaced by a full implementation in a subsequent issue.
 */
const CategoriesPage: React.FC = () => (
  <section aria-labelledby="categories-heading">
    <h1 id="categories-heading">Categories</h1>
    <p>Categories list coming soon.</p>
  </section>
);

/**
 * Root application component.
 * Sets up React Router v6 with routes for Home, Articles, and Categories.
 */
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/articles" element={<ArticlesPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};

export default App;
