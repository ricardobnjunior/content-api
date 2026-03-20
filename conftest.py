"""Root-level pytest configuration and shared fixtures."""

import os

# Remove any env vars that might interfere with default Settings tests
# These will be set by specific tests or test infrastructure as needed
for _var in ("DATABASE_URL", "SECRET_KEY", "ENVIRONMENT"):
    os.environ.pop(_var, None)

# Also ensure there's no .env file that would override defaults
import pathlib
_env_file = pathlib.Path(".env")
_env_backup = None
if _env_file.exists():
    _env_backup = _env_file.read_text()
    _env_file.unlink()

import pytest  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

from app.database import SessionLocal, create_tables  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> None:
    """Create all database tables once per test session."""
    create_tables()


@pytest.fixture
def client() -> TestClient:
    """Return a synchronous test client for the FastAPI application.

    Returns:
        TestClient: Starlette test client wrapping the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def db_session():
    """Yield a database session and close it after the test.

    Yields:
        Session: SQLAlchemy synchronous database session connected to the test DB.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
