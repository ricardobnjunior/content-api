"""Root conftest.py — configures test environment."""

import os
import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once for the entire test session."""
    from app.database import Base, create_tables, engine
    create_tables()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    """Provide a Starlette TestClient for the FastAPI app."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("ENVIRONMENT", "test")
        mp.setenv("DATABASE_URL", "sqlite:///test.db")
        mp.setenv("SECRET_KEY", "test-secret-key-not-for-production")
        from app.config import get_settings
        get_settings.cache_clear()
        from app.main import create_app
        test_app = create_app()
        with TestClient(test_app) as test_client:
            yield test_client
        get_settings.cache_clear()


@pytest.fixture
def db_session() -> Session:
    """Provide a SQLAlchemy Session for direct database operations in tests."""
    from app.database import SessionLocal
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
