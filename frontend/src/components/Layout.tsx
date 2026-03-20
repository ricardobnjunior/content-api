import React from "react";
import { Link } from "react-router-dom";

interface LayoutProps {
  /** Page content to render inside the main area. */
  children: React.ReactNode;
}

/**
 * Shared layout component that wraps all pages.
 * Renders a header with navigation links and a main content area.
 */
const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <>
      <header>
        <nav aria-label="Main navigation">
          <span className="brand">News CMS</span>
          <Link to="/" aria-label="Go to home page">
            Home
          </Link>
          <Link to="/articles" aria-label="Go to articles page">
            Articles
          </Link>
          <Link to="/categories" aria-label="Go to categories page">
            Categories
          </Link>
        </nav>
      </header>
      <main>{children}</main>
    </>
  );
};

export default Layout;
