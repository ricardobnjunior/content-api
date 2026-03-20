import React from "react";
import { Link } from "react-router-dom";

/**
 * Home page — landing page with navigation links to main sections.
 */
const HomePage: React.FC = () => {
  return (
    <section aria-labelledby="home-heading">
      <h1 id="home-heading">Welcome to News CMS</h1>
      <p>
        A simple content management system for news articles and categories.
      </p>
      <nav aria-label="Section links" className="home-links">
        <Link to="/articles">Browse Articles</Link>
        <Link to="/categories">Browse Categories</Link>
      </nav>
    </section>
  );
};

export default HomePage;
