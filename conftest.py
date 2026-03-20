"""Root-level pytest configuration and shared fixtures."""

import os

# Set test environment variables BEFORE importing any application modules.
# This ensures pydantic-settings reads these values at Settings instantiation time.
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ENVIRONMENT", "development")

import pytest  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, create_tables, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> None:
    """Create all tables in the test database before running the test suite.

    This fixture runs once per session and ensures the schema exists.
    """
    create_tables()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    """Return a synchronous TestClient wrapping the FastAPI application.

    Returns:
        TestClient: A Starlette test client for making HTTP requests.
    """
    return TestClient(app)


@pytest.fixture
def db_session() -> Session:
    """Yield a database session connected to the test database.

    The session is rolled back and closed after each test to keep
    test cases isolated.

    Yields:
        Session: A SQLAlchemy synchronous session bound to the test engine.
    """
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
