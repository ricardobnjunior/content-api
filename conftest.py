"""Shared test fixtures for the articles API test suite."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables before the test session and drop them after.

    Yields:
        None
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Provide a transactional database session that rolls back after each test.

    Yields:
        SQLAlchemy Session instance.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Provide a test HTTP client with overridden database dependency.

    Args:
        db_session: Transactional test database session.

    Yields:
        FastAPI TestClient instance.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def override_upload_dir(tmp_path):
    """Override the upload directory setting to use a temporary path for each test.

    Args:
        tmp_path: pytest built-in temporary directory fixture.

    Yields:
        None — restores original upload_dir after each test.
    """
    settings = get_settings()
    original_upload_dir = settings.upload_dir
    settings.upload_dir = str(tmp_path / "uploads")
    os.makedirs(settings.upload_dir, exist_ok=True)
    yield
    settings.upload_dir = original_upload_dir
