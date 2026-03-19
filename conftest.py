"""Pytest configuration and shared fixtures."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, create_tables, engine  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402

# Import all models so they are registered with Base.metadata
import app.models.article  # noqa: E402, F401
import app.models.category  # noqa: E402, F401


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop them after."""
    create_tables()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """Provide a SQLAlchemy session for direct DB access in tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(setup_database) -> TestClient:
    """Provide a FastAPI TestClient with a fresh database."""
    with TestClient(fastapi_app) as c:
        yield c
