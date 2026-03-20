import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import ArticlesPage from './pages/ArticlesPage';

/**
 * Root application component.
 * Defines all client-side routes using React Router v6.
 */
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Redirect root to articles list */}
        <Route path="/" element={<Navigate to="/articles" replace />} />

        {/* Articles listing page */}
        <Route path="/articles" element={<ArticlesPage />} />

        {/* Article detail page placeholder — to be implemented in a future issue */}
        {/* <Route path="/articles/:id" element={<ArticleDetailPage />} /> */}
      </Routes>
    </BrowserRouter>
  );
};

export default App;
