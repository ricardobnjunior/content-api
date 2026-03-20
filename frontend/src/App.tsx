import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import CategoriesPage from './pages/CategoriesPage';

/**
 * Root application component.
 * Defines the top-level routing structure.
 *
 * @returns The application with routing configured.
 */
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/categories" element={<CategoriesPage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
