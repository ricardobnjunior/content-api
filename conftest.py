"""Root-level pytest configuration and shared fixtures."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ENVIRONMENT", "development")

from app.database import SessionLocal, create_tables  # noqa: E402
from app.main import app  # noqa: E402

import pytest  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> None:
    """Create all database tables once for the test session."""
    create_tables()


@pytest.fixture
def client() -> TestClient:
    """Provide a synchronous HTTP test client for the FastAPI application.

    Returns:
        TestClient: A Starlette test client bound to the app.
    """
    return TestClient(app)


@pytest.fixture
def db_session():
    """Yield a database session for use in tests.

    Yields:
        Session: An active SQLAlchemy session that is closed after the test.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
