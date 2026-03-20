"""Tests for the API router integration."""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_router.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.main import app  # noqa: E402
from app.database import get_db, Base  # noqa: E402
from app.models.article import Article  # noqa: E402
from app.models.category import Category  # ensure all models loaded  # noqa: E402
import app.api.router as router_module  # noqa: E402
import app.api.endpoints.recommendations as recommendations  # noqa: E402
import app.ml.similarity as similarity  # noqa: E402

# ---------------------------------------------------------------------------
# DB setup
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def add_article(session, title: str, content: str, status: str = "published") -> Article:
    a = Article(title=title, content=content, status=status)
    session.add(a)
    session.commit()
    session.refresh(a)
    return a


# ---------------------------------------------------------------------------
# Router presence tests
# ---------------------------------------------------------------------------

class TestRouterRegistration:
    """Verify all routers respond correctly."""

    def test_articles_endpoint_registered(self, client):
        """GET /api/v1/articles/ should not return 404."""
        resp = client.get("/api/v1/articles/")
        assert resp.status_code != 404

    def test_categories_endpoint_registered(self, client):
        """GET /api/v1/categories/ should not return 404."""
        resp = client.get("/api/v1/categories/")
        assert resp.status_code != 404

    def test_suggestions_endpoint_registered(self, client):
        """GET /api/v1/suggestions/ should not return 404."""
        resp = client.get("/api/v1/suggestions/")
        assert resp.status_code != 404

    def test_recommendations_endpoint_registered(self, client, db_session):
        """GET /api/v1/recommendations/{id}/similar should not return 404 for valid article."""
        article = add_article(
            db_session,
            "Test Article Router",
            "Testing that the recommendations router is correctly registered.",
        )
        resp = client.get(f"/api/v1/recommendations/{article.id}/similar")
        assert resp.status_code == 200

    def test_recommendations_wrong_prefix_is_404(self, client):
        """Recommendations should NOT be accessible at /api/v1/articles/{id}/similar."""
        resp = client.get("/api/v1/articles/1/similar")
        assert resp.status_code == 404

    def test_recommendations_response_schema(self, client, db_session):
        """Recommendations endpoint returns the expected JSON structure."""
        article = add_article(
            db_session,
            "Schema Test Article",
            "This article tests the response schema of the recommendations endpoint.",
        )
        resp = client.get(f"/api/v1/recommendations/{article.id}/similar")
        assert resp.status_code == 200
        body = resp.json()
        assert set(body.keys()) >= {"article_id", "similar_articles"}


class TestRouterImports:
    """Verify that the router module imports correctly."""

    def test_router_importable(self):
        """The app.api.router module should be importable."""
        assert hasattr(router_module, "router")

    def test_recommendations_router_importable(self):
        """The recommendations endpoint module should be importable."""
        assert hasattr(recommendations, "router")

    def test_similarity_module_importable(self):
        """The ml.similarity module should be importable."""
        assert hasattr(similarity, "find_similar_articles")
        assert hasattr(similarity, "SimilarArticle")
