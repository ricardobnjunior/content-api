"""Tests for the article recommendations (similar articles) endpoint."""

import os
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_recommendations.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app  # noqa: E402
from app.database import get_db, Base  # noqa: E402
from app.models.article import Article  # noqa: E402
from app.models.category import Category  # ensure all models loaded  # noqa: E402

# ---------------------------------------------------------------------------
# Test database setup
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite:///./test_recommendations.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Dependency override that uses the test SQLite database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Provide a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    """Provide a synchronous test client."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def create_article(
    db,
    title: str,
    content: str,
    status: str = "published",
    category_id: int = None,
) -> Article:
    """Create and persist a test article."""
    article = Article(
        title=title,
        content=content,
        status=status,
        category_id=category_id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSingleArticle:
    """Tests for the edge case where only one published article exists."""

    def test_single_article_returns_empty_list(self, client, db):
        """When only one published article exists, similar_articles should be empty."""
        article = create_article(
            db,
            title="Python programming basics",
            content="This article covers Python fundamentals including variables and loops.",
        )

        response = client.get(f"/api/v1/recommendations/{article.id}/similar")
        assert response.status_code == 200
        data = response.json()
        assert data["article_id"] == article.id
        assert data["similar_articles"] == []


class TestSimilarArticlesReturned:
    """Tests for the main similarity functionality."""

    def test_similar_articles_returned_with_scores(self, client, db):
        """With multiple related articles, response should contain scored results."""
        base = create_article(
            db,
            title="Machine learning with Python",
            content=(
                "Machine learning is a subset of artificial intelligence. "
                "Python is the most popular language for machine learning. "
                "Libraries like scikit-learn and tensorflow are widely used."
            ),
        )
        create_article(
            db,
            title="Python machine learning tutorial",
            content=(
                "This tutorial covers machine learning algorithms in Python. "
                "We use scikit-learn for machine learning model training. "
                "Machine learning models require data preprocessing."
            ),
        )
        create_article(
            db,
            title="Introduction to artificial intelligence",
            content=(
                "Artificial intelligence encompasses machine learning and deep learning. "
                "Python libraries support artificial intelligence development. "
                "AI and machine learning are transforming industries."
            ),
        )

        response = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert response.status_code == 200

        data = response.json()
        assert data["article_id"] == base.id
        assert isinstance(data["similar_articles"], list)
        assert len(data["similar_articles"]) > 0

        for item in data["similar_articles"]:
            assert "id" in item
            assert "title" in item
            assert "similarity_score" in item
            assert isinstance(item["similarity_score"], float)
            assert 0.0 < item["similarity_score"] <= 1.0
            assert item["id"] != base.id

    def test_results_ordered_by_score_descending(self, client, db):
        """Similar articles should be ordered by similarity score descending."""
        base = create_article(
            db,
            title="Deep learning neural networks",
            content=(
                "Deep learning uses neural networks with multiple layers. "
                "Neural networks are inspired by the human brain. "
                "Deep learning requires large amounts of training data."
            ),
        )
        create_article(
            db,
            title="Neural network deep learning guide",
            content=(
                "Neural networks in deep learning have input hidden output layers. "
                "Deep learning neural networks achieve state of the art results. "
                "Training deep learning neural networks requires GPUs."
            ),
        )
        create_article(
            db,
            title="Introduction to machine learning concepts",
            content=(
                "Machine learning involves training models on data. "
                "Supervised learning uses labeled training examples. "
                "Model evaluation uses metrics like accuracy."
            ),
        )

        response = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert response.status_code == 200
        data = response.json()

        scores = [item["similarity_score"] for item in data["similar_articles"]]
        assert scores == sorted(scores, reverse=True)


class TestNotFound:
    """Tests for non-existent article IDs."""

    def test_nonexistent_article_returns_404(self, client, db):
        """A non-existent article ID should return HTTP 404."""
        response = client.get("/api/v1/recommendations/99999/similar")
        assert response.status_code == 404

    def test_404_response_has_detail(self, client, db):
        """404 response should include a detail message."""
        response = client.get("/api/v1/recommendations/99999/similar")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestLimitParameter:
    """Tests for the limit query parameter."""

    def _create_many_articles(self, db, base_title: str, base_content: str, count: int):
        """Helper to create multiple related articles."""
        articles = []
        for i in range(count):
            a = create_article(
                db,
                title=f"{base_title} part {i}",
                content=f"{base_content} Section {i} discusses more details about {base_title.lower()}.",
            )
            articles.append(a)
        return articles

    def test_limit_parameter_default(self, client, db):
        """Without explicit limit, at most 5 articles should be returned."""
        base = create_article(
            db,
            title="Python programming",
            content="Python is a versatile programming language used for web development machine learning and scripting.",
        )
        self._create_many_articles(
            db,
            "Python programming guide",
            "Python programming language is versatile for web development machine learning scripting automation.",
            count=7,
        )

        response = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert response.status_code == 200
        data = response.json()
        assert len(data["similar_articles"]) <= 5

    def test_limit_parameter_custom(self, client, db):
        """With ?limit=2, at most 2 articles should be returned."""
        base = create_article(
            db,
            title="Data science with Python",
            content="Data science uses Python for statistical analysis visualization and modeling.",
        )
        self._create_many_articles(
            db,
            "Data science Python tutorial",
            "Data science with Python involves statistical analysis visualization modeling and machine learning.",
            count=6,
        )

        response = client.get(f"/api/v1/recommendations/{base.id}/similar?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["similar_articles"]) <= 2

    def test_limit_parameter_large(self, client, db):
        """With a large limit, only available similar articles are returned."""
        base = create_article(
            db,
            title="FastAPI web framework",
            content="FastAPI is a modern Python web framework for building APIs.",
        )
        create_article(
            db,
            title="FastAPI tutorial for beginners",
            content="FastAPI framework makes building Python web APIs fast and easy.",
        )

        response = client.get(f"/api/v1/recommendations/{base.id}/similar?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert len(data["similar_articles"]) <= 1


class TestDraftExclusion:
    """Tests that draft articles are excluded from recommendations."""

    def test_draft_articles_excluded(self, client, db):
        """Draft articles should never appear in similar_articles results."""
        base = create_article(
            db,
            title="Python web development",
            content=(
                "Python web development uses frameworks like Django and Flask. "
                "Web development in Python is popular for backend services."
            ),
        )
        draft = create_article(
            db,
            title="Python web development draft",
            content=(
                "Python web development uses frameworks like Django and Flask. "
                "Web development in Python is popular for backend services. Draft content."
            ),
            status="draft",
        )
        published = create_article(
            db,
            title="Flask Python framework guide",
            content=(
                "Flask is a lightweight Python framework for web development. "
                "Python web development with Flask is beginner friendly."
            ),
            status="published",
        )

        response = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert response.status_code == 200
        data = response.json()

        result_ids = [item["id"] for item in data["similar_articles"]]
        assert draft.id not in result_ids

    def test_only_draft_articles_available(self, client, db):
        """If only draft articles exist besides the target, result should be empty."""
        base = create_article(
            db,
            title="Python scripting",
            content="Python is great for scripting and automation tasks.",
        )
        create_article(
            db,
            title="Python scripting guide",
            content="Python scripting and automation are very useful skills.",
            status="draft",
        )

        response = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert response.status_code == 200
        data = response.json()
        assert data["similar_articles"] == []


class TestLowSimilarityFiltering:
    """Tests that articles with very low similarity scores are filtered out."""

    def test_low_similarity_articles_filtered(self, client, db):
        """Articles with cosine similarity < 0.1 should not appear in results."""
        base = create_article(
            db,
            title="Quantum physics and relativity",
            content=(
                "Quantum mechanics describes the behavior of subatomic particles. "
                "General relativity describes the structure of spacetime and gravity. "
                "These two theories form the foundation of modern physics."
            ),
        )
        create_article(
            db,
            title="Cooking pasta carbonara",
            content=(
                "Pasta carbonara is an Italian dish made with eggs cheese and pancetta. "
                "Boil the pasta until al dente then mix with the sauce. "
                "Season with black pepper and serve immediately."
            ),
        )

        response = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert response.status_code == 200
        data = response.json()

        for item in data["similar_articles"]:
            assert item["similarity_score"] >= 0.1


class TestRouterIntegrity:
    """Tests that all existing routers remain accessible after adding recommendations."""

    def test_articles_router_accessible(self, client, db):
        """The /api/v1/articles/ endpoint should still be accessible."""
        response = client.get("/api/v1/articles/")
        assert response.status_code != 404

    def test_categories_router_accessible(self, client, db):
        """The /api/v1/categories/ endpoint should still be accessible."""
        response = client.get("/api/v1/categories/")
        assert response.status_code != 404

    def test_suggestions_router_accessible(self, client, db):
        """The /api/v1/suggestions/ endpoint should still be accessible."""
        response = client.get("/api/v1/suggestions/")
        assert response.status_code != 404

    def test_recommendations_router_prefix(self, client, db):
        """The recommendations endpoint should be at /api/v1/recommendations/{id}/similar."""
        article = create_article(
            db,
            title="Test article for routing",
            content="This article tests that the recommendations endpoint is correctly routed.",
        )

        response = client.get(f"/api/v1/recommendations/{article.id}/similar")
        assert response.status_code == 200
        data = response.json()
        assert "article_id" in data
        assert "similar_articles" in data

    def test_recommendations_router_not_at_wrong_prefix(self, client, db):
        """Recommendations endpoint should NOT be accessible at /api/v1/articles/{id}/similar."""
        response = client.get("/api/v1/articles/1/similar")
        assert response.status_code == 404
