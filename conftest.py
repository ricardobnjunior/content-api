"""Shared test fixtures for the articles API test suite."""

import os

import pytest
from fastapi.testclient import TestClient

# Set required environment variables BEFORE importing any app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_articles.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables before the test session and drop them after.

    Yields:
        None
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a clean database session for each test.

    Rolls back the transaction after each test to isolate state.

    Yields:
        Session: SQLAlchemy database session.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session, override_upload_dir):
    """Provide a TestClient with the database session overridden.

    Args:
        db_session: Isolated database session fixture.
        override_upload_dir: Upload directory override fixture.

    Yields:
        TestClient: Sync test client for the FastAPI app.
    """
    from app.database import get_db  # noqa: E402

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def override_upload_dir(tmp_path):
    """Override the upload directory setting to use a temporary path.

    Ensures uploaded files during tests are isolated to ``tmp_path`` and
    cleaned up automatically.

    Args:
        tmp_path: pytest built-in temporary directory fixture.

    Yields:
        str: Path to the temporary upload directory.
    """
    upload_path = str(tmp_path / "uploads")
    os.makedirs(upload_path, exist_ok=True)

    from app.config import get_settings  # noqa: E402

    settings = get_settings()
    original_upload_dir = settings.upload_dir
    settings.upload_dir = upload_path

    yield upload_path

    settings.upload_dir = original_upload_dir
