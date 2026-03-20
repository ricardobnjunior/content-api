"""Integration tests for the /api/v1/recommendations/{article_id}/similar endpoint."""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_rec_endpoint.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.main import app  # noqa: E402
from app.database import get_db, Base  # noqa: E402
from app.models.article import Article  # noqa: E402
from app.models.category import Category  # ensure all models loaded  # noqa: E402

# ---------------------------------------------------------------------------
# Test database wiring
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Dependency override using the in-memory test database."""
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    """Recreate tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Provide a test session for direct DB manipulation."""
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    """Provide a sync TestClient."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def add_article(session, title: str, content: str, status: str = "published") -> Article:
    """Add and return a persisted Article."""
    a = Article(title=title, content=content, status=status)
    session.add(a)
    session.commit()
    session.refresh(a)
    return a


# ---------------------------------------------------------------------------
# 404 Tests
# ---------------------------------------------------------------------------

class TestNotFound:
    def test_nonexistent_article_404(self, client):
        """Requesting similar articles for a missing article returns 404."""
        resp = client.get("/api/v1/recommendations/99999/similar")
        assert resp.status_code == 404

    def test_404_has_detail_field(self, client):
        """404 response body must have a 'detail' key."""
        resp = client.get("/api/v1/recommendations/42/similar")
        assert resp.status_code == 404
        body = resp.json()
        assert "detail" in body

    def test_draft_article_requested_directly_still_404_if_not_in_db(self, client, db_session):
        """Requesting a non-existent article even with drafts present returns 404."""
        add_article(db_session, "Draft Article", "Draft content only.", status="draft")
        resp = client.get("/api/v1/recommendations/99998/similar")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Response structure tests
# ---------------------------------------------------------------------------

class TestResponseStructure:
    def test_response_has_required_fields(self, client, db_session):
        """Response must contain article_id and similar_articles fields."""
        article = add_article(db_session, "Solo Article", "This is the only article.")
        resp = client.get(f"/api/v1/recommendations/{article.id}/similar")
        assert resp.status_code == 200
        body = resp.json()
        assert "article_id" in body
        assert "similar_articles" in body

    def test_article_id_matches_requested(self, client, db_session):
        """article_id in response should match the requested article ID."""
        article = add_article(db_session, "Test Article", "Some test content.")
        resp = client.get(f"/api/v1/recommendations/{article.id}/similar")
        assert resp.status_code == 200
        body = resp.json()
        assert body["article_id"] == article.id

    def test_similar_articles_is_list(self, client, db_session):
        """similar_articles field must be a list."""
        article = add_article(db_session, "Test Article", "Test content here.")
        resp = client.get(f"/api/v1/recommendations/{article.id}/similar")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body["similar_articles"], list)

    def test_similar_article_item_structure(self, client, db_session):
        """Each item in similar_articles must have id, title, similarity_score."""
        base = add_article(
            db_session,
            "Python Basics",
            "Python is a popular programming language for beginners and experts.",
        )
        add_article(
            db_session,
            "Python Programming Guide",
            "Python programming guide for beginners covers variables functions and classes.",
        )

        resp = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert resp.status_code == 200
        body = resp.json()

        for item in body["similar_articles"]:
            assert "id" in item
            assert "title" in item
            assert "similarity_score" in item
            assert isinstance(item["id"], int)
            assert isinstance(item["title"], str)
            assert isinstance(item["similarity_score"], float)


# ---------------------------------------------------------------------------
# Single article tests
# ---------------------------------------------------------------------------

class TestSingleArticle:
    def test_single_article_empty_results(self, client, db_session):
        """Only one published article → similar_articles is empty list."""
        article = add_article(
            db_session,
            "Lone Article",
            "This is the only published article in the system.",
        )
        resp = client.get(f"/api/v1/recommendations/{article.id}/similar")
        assert resp.status_code == 200
        assert resp.json()["similar_articles"] == []

    def test_single_published_with_draft_siblings_is_empty(self, client, db_session):
        """One published + many drafts → similar_articles is empty list."""
        base = add_article(
            db_session,
            "The Only Published Article",
            "Only this article has published status in the database.",
        )
        for i in range(3):
            add_article(
                db_session,
                f"Draft Article {i}",
                f"This is draft content number {i}.",
                status="draft",
            )
        resp = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert resp.status_code == 200
        assert resp.json()["similar_articles"] == []


# ---------------------------------------------------------------------------
# Multiple articles tests
# ---------------------------------------------------------------------------

class TestMultipleArticles:
    def test_similar_articles_returned(self, client, db_session):
        """Multiple related articles → similar_articles has items."""
        base = add_article(
            db_session,
            "Python Machine Learning",
            "Python machine learning with scikit-learn and numpy for data analysis.",
        )
        add_article(
            db_session,
            "Machine Learning Python Guide",
            "Machine learning in Python using scikit-learn numpy and pandas for models.",
        )
        add_article(
            db_session,
            "Python Data Science",
            "Data science with Python uses machine learning scikit-learn and visualization.",
        )

        resp = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["similar_articles"]) > 0

    def test_results_ordered_by_score_desc(self, client, db_session):
        """Results must be ordered by similarity_score descending."""
        base = add_article(
            db_session,
            "FastAPI Development",
            "FastAPI is a fast Python web framework for building RESTful APIs efficiently.",
        )
        add_article(
            db_session,
            "FastAPI REST API Tutorial",
            "Build fast REST APIs with FastAPI Python web framework efficiently.",
        )
        add_article(
            db_session,
            "Web APIs Overview",
            "Web APIs use HTTP REST and JSON for communication between services.",
        )

        resp = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert resp.status_code == 200
        scores = [item["similarity_score"] for item in resp.json()["similar_articles"]]
        assert scores == sorted(scores, reverse=True)

    def test_target_not_in_results(self, client, db_session):
        """The queried article should never appear in its own similar list."""
        base = add_article(
            db_session,
            "NLP Natural Language Processing",
            "Natural language processing uses machine learning for text understanding.",
        )
        add_article(
            db_session,
            "NLP Text Processing Guide",
            "Natural language processing guide covers tokenization and embeddings.",
        )

        resp = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert resp.status_code == 200
        result_ids = [item["id"] for item in resp.json()["similar_articles"]]
        assert base.id not in result_ids


# ---------------------------------------------------------------------------
# Limit parameter tests
# ---------------------------------------------------------------------------

class TestLimitParameter:
    def _add_related_articles(self, session, count: int):
        """Create `count` related published articles plus a base article."""
        base = add_article(
            session,
            "Base Topic Article",
            "Base topic covers machine learning deep learning Python and data science fundamentals.",
        )
        for i in range(count):
            add_article(
                session,
                f"Related Topic Article {i}",
                f"Related topic {i} covers machine learning deep learning Python data science fundamentals.",
            )
        return base

    def test_default_limit_is_five(self, client, db_session):
        """Without specifying limit, at most 5 results are returned."""
        base = self._add_related_articles(db_session, count=8)
        resp = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert resp.status_code == 200
        assert len(resp.json()["similar_articles"]) <= 5

    def test_custom_limit_two(self, client, db_session):
        """With limit=2, at most 2 results are returned."""
        base = self._add_related_articles(db_session, count=6)
        resp = client.get(f"/api/v1/recommendations/{base.id}/similar?limit=2")
        assert resp.status_code == 200
        assert len(resp.json()["similar_articles"]) <= 2

    def test_limit_one(self, client, db_session):
        """With limit=1, at most 1 result is returned."""
        base = self._add_related_articles(db_session, count=4)
        resp = client.get(f"/api/v1/recommendations/{base.id}/similar?limit=1")
        assert resp.status_code == 200
        assert len(resp.json()["similar_articles"]) <= 1

    def test_limit_zero_rejected(self, client, db_session):
        """limit=0 is below the minimum (1) and should return 422."""
        article = add_article(db_session, "Article", "Content for validation test.")
        resp = client.get(f"/api/v1/recommendations/{article.id}/similar?limit=0")
        assert resp.status_code == 422

    def test_limit_above_max_rejected(self, client, db_session):
        """limit=51 exceeds the maximum (50) and should return 422."""
        article = add_article(db_session, "Article", "Content for validation test.")
        resp = client.get(f"/api/v1/recommendations/{article.id}/similar?limit=51")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Draft exclusion tests
# ---------------------------------------------------------------------------

class TestDraftExclusion:
    def test_drafts_not_in_results(self, client, db_session):
        """Draft articles should never appear in recommendation results."""
        base = add_article(
            db_session,
            "Python Flask Web Framework",
            "Flask is a lightweight Python web framework for building web applications.",
        )
        draft = add_article(
            db_session,
            "Python Flask Tutorial Draft",
            "Flask Python web framework tutorial for building web applications and APIs.",
            status="draft",
        )
        add_article(
            db_session,
            "Python Flask REST API",
            "Build REST APIs with Python Flask web framework for web applications.",
        )

        resp = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert resp.status_code == 200
        result_ids = [item["id"] for item in resp.json()["similar_articles"]]
        assert draft.id not in result_ids


# ---------------------------------------------------------------------------
# Low similarity filtering tests
# ---------------------------------------------------------------------------

class TestLowSimilarityFiltering:
    def test_low_similarity_excluded(self, client, db_session):
        """Results should all have similarity_score >= 0.1."""
        base = add_article(
            db_session,
            "Astrophysics and Cosmology",
            "Astrophysics studies celestial objects stars galaxies black holes and the cosmos.",
        )
        add_article(
            db_session,
            "Italian Cooking Recipes",
            "Italian cooking recipes include pizza pasta risotto tiramisu and gelato desserts.",
        )

        resp = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert resp.status_code == 200
        for item in resp.json()["similar_articles"]:
            assert item["similarity_score"] >= 0.1

    def test_all_scores_are_valid_floats(self, client, db_session):
        """All similarity scores should be valid float values between 0 and 1."""
        base = add_article(
            db_session,
            "Cloud Computing AWS",
            "Cloud computing with AWS includes EC2 S3 Lambda and RDS for scalable applications.",
        )
        add_article(
            db_session,
            "AWS Cloud Services Guide",
            "AWS cloud services EC2 S3 Lambda and RDS provide scalable cloud computing solutions.",
        )

        resp = client.get(f"/api/v1/recommendations/{base.id}/similar")
        assert resp.status_code == 200
        for item in resp.json()["similar_articles"]:
            score = item["similarity_score"]
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
