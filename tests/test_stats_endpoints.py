"""Integration tests for stats endpoints using a real SQLite test database."""

import os
import tempfile
from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

# We need to patch DATABASE_URL before importing app modules
# Use a temp file so each test session gets a fresh DB


@pytest.fixture(scope="module")
def test_db_path():
    """Provide a temporary SQLite database file path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    # Cleanup
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture(scope="module")
def test_engine(test_db_path):
    """Create a SQLAlchemy engine pointed at the temp SQLite file."""
    db_url = f"sqlite:///{test_db_path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    return engine


@pytest.fixture(scope="module")
def setup_tables(test_engine):
    """Create all tables using the app's Base metadata."""
    from app.models.article import Base as ArticleBase
    from app.models.category import Base as CategoryBase

    ArticleBase.metadata.create_all(bind=test_engine)
    CategoryBase.metadata.create_all(bind=test_engine)
    return test_engine


@pytest.fixture(scope="module")
def client(test_db_path, setup_tables):
    """Create a TestClient with overridden get_db dependency."""
    db_url = f"sqlite:///{test_db_path}"

    with patch.dict(
        os.environ,
        {"DATABASE_URL": db_url, "SECRET_KEY": "testsecretkey"},
        clear=False,
    ):
        from app.main import app  # noqa: E402
        from app.database import get_db  # noqa: E402

        engine = create_engine(db_url, connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as c:
            yield c

        app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def db_session(test_db_path, setup_tables):
    """Provide a DB session for seeding test data."""
    db_url = f"sqlite:///{test_db_path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def clear_tables(session):
    """Delete all rows from all relevant tables."""
    from app.models.category import article_categories  # noqa: E402
    session.execute(article_categories.delete())
    session.query(__import__("app.models.article", fromlist=["Article"]).Article).delete()
    session.query(__import__("app.models.category", fromlist=["Category"]).Category).delete()
    session.commit()


class TestStatsEndpointEmpty:
    """Test stats endpoint with an empty database."""

    def test_empty_database_returns_zeros(self, client, db_session):
        clear_tables(db_session)
        response = client.get("/api/v1/stats/")
        assert response.status_code == 200
        data = response.json()
        assert data["total_articles"] == 0
        assert data["by_status"] == {}
        assert data["by_category"] == []
        assert data["total_categories"] == 0
        assert data["latest_article"] is None

    def test_empty_timeline(self, client, db_session):
        clear_tables(db_session)
        response = client.get("/api/v1/stats/timeline")
        assert response.status_code == 200
        data = response.json()
        assert data["timeline"] == []


class TestStatsEndpointWithData:
    """Test stats endpoints with seeded data."""

    @pytest.fixture(autouse=True)
    def seed_data(self, db_session):
        """Seed the database with test articles and categories."""
        from app.models.article import Article  # noqa: E402
        from app.models.category import Category, article_categories  # noqa: E402

        clear_tables(db_session)

        # Create categories
        cat_tech = Category(name="Technology")
        cat_science = Category(name="Science")
        cat_empty = Category(name="EmptyCategory")
        db_session.add_all([cat_tech, cat_science, cat_empty])
        db_session.flush()

        # Create articles with different statuses and created_at dates
        a1 = Article(
            title="Draft Article 1",
            content="Content 1",
            status="draft",
            created_at=datetime(2026, 1, 5, 10, 0, 0),
            updated_at=datetime(2026, 1, 5, 10, 0, 0),
        )
        a2 = Article(
            title="Draft Article 2",
            content="Content 2",
            status="draft",
            created_at=datetime(2026, 1, 15, 12, 0, 0),
            updated_at=datetime(2026, 1, 15, 12, 0, 0),
        )
        a3 = Article(
            title="Published Article 1",
            content="Content 3",
            status="published",
            created_at=datetime(2026, 2, 10, 8, 0, 0),
            updated_at=datetime(2026, 2, 10, 8, 0, 0),
        )
        a4 = Article(
            title="Published Article 2",
            content="Content 4",
            status="published",
            created_at=datetime(2026, 2, 20, 9, 0, 0),
            updated_at=datetime(2026, 2, 20, 9, 0, 0),
        )
        a5 = Article(
            title="Latest Published",
            content="Content 5",
            status="published",
            created_at=datetime(2026, 3, 20, 10, 0, 0),
            updated_at=datetime(2026, 3, 20, 10, 0, 0),
        )
        db_session.add_all([a1, a2, a3, a4, a5])
        db_session.flush()

        # Associate articles with categories
        db_session.execute(
            article_categories.insert().values(
                [
                    {"article_id": a1.id, "category_id": cat_tech.id},
                    {"article_id": a2.id, "category_id": cat_tech.id},
                    {"article_id": a3.id, "category_id": cat_tech.id},
                    {"article_id": a4.id, "category_id": cat_science.id},
                    {"article_id": a5.id, "category_id": cat_science.id},
                ]
            )
        )
        db_session.commit()

        yield

        clear_tables(db_session)

    def test_total_articles_count(self, client):
        response = client.get("/api/v1/stats/")
        assert response.status_code == 200
        data = response.json()
        assert data["total_articles"] == 5

    def test_by_status_breakdown(self, client):
        response = client.get("/api/v1/stats/")
        assert response.status_code == 200
        data = response.json()
        assert data["by_status"]["draft"] == 2
        assert data["by_status"]["published"] == 3

    def test_total_categories(self, client):
        response = client.get("/api/v1/stats/")
        assert response.status_code == 200
        data = response.json()
        assert data["total_categories"] == 3

    def test_by_category_counts(self, client):
        response = client.get("/api/v1/stats/")
        assert response.status_code == 200
        data = response.json()
        # Only categories with articles appear
        by_category = data["by_category"]
        cat_names = {c["category_name"]: c["article_count"] for c in by_category}
        assert cat_names["Technology"] == 3
        assert cat_names["Science"] == 2
        # EmptyCategory has no articles, should not appear
        assert "EmptyCategory" not in cat_names

    def test_by_category_ordered_by_count_desc(self, client):
        response = client.get("/api/v1/stats/")
        assert response.status_code == 200
        data = response.json()
        by_category = data["by_category"]
        # First entry should be the category with most articles
        assert by_category[0]["category_name"] == "Technology"
        assert by_category[0]["article_count"] == 3

    def test_latest_article(self, client):
        response = client.get("/api/v1/stats/")
        assert response.status_code == 200
        data = response.json()
        assert data["latest_article"] is not None
        assert data["latest_article"]["title"] == "Latest Published"
        assert data["latest_article"]["id"] is not None

    def test_latest_article_has_required_fields(self, client):
        response = client.get("/api/v1/stats/")
        assert response.status_code == 200
        data = response.json()
        latest = data["latest_article"]
        assert "id" in latest
        assert "title" in latest
        assert "created_at" in latest

    def test_timeline_groups_by_month(self, client):
        response = client.get("/api/v1/stats/timeline")
        assert response.status_code == 200
        data = response.json()
        timeline = data["timeline"]
        months = {entry["month"]: entry["count"] for entry in timeline}
        assert months.get("2026-01") == 2
        assert months.get("2026-02") == 2
        assert months.get("2026-03") == 1

    def test_timeline_ordered_chronologically(self, client):
        response = client.get("/api/v1/stats/timeline")
        assert response.status_code == 200
        data = response.json()
        timeline = data["timeline"]
        months = [entry["month"] for entry in timeline]
        assert months == sorted(months)

    def test_timeline_entry_structure(self, client):
        response = client.get("/api/v1/stats/timeline")
        assert response.status_code == 200
        data = response.json()
        for entry in data["timeline"]:
            assert "month" in entry
            assert "count" in entry
            assert isinstance(entry["count"], int)
            # month format should be YYYY-MM
            assert len(entry["month"]) == 7
            assert entry["month"][4] == "-"


class TestStatsEndpointSingleArticle:
    """Test stats with a single article."""

    @pytest.fixture(autouse=True)
    def seed_single(self, db_session):
        from app.models.article import Article  # noqa: E402

        clear_tables(db_session)

        article = Article(
            title="Only Article",
            content="Solo content",
            status="published",
            created_at=datetime(2026, 5, 1, 0, 0, 0),
            updated_at=datetime(2026, 5, 1, 0, 0, 0),
        )
        db_session.add(article)
        db_session.commit()

        yield

        clear_tables(db_session)

    def test_single_article_stats(self, client):
        response = client.get("/api/v1/stats/")
        assert response.status_code == 200
        data = response.json()
        assert data["total_articles"] == 1
        assert data["by_status"] == {"published": 1}
        assert data["latest_article"]["title"] == "Only Article"
        assert data["total_categories"] == 0

    def test_single_article_timeline(self, client):
        response = client.get("/api/v1/stats/timeline")
        assert response.status_code == 200
        data = response.json()
        assert len(data["timeline"]) == 1
        assert data["timeline"][0]["month"] == "2026-05"
        assert data["timeline"][0]["count"] == 1
