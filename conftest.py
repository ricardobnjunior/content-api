"""Root conftest for test suite — sets up in-memory SQLite DB and TestClient."""

import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

# Point to an in-memory SQLite DB before any app imports
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_app.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("OPENROUTER_API_KEY", "test-api-key")
os.environ.setdefault("OPENROUTER_MODEL", "google/gemini-2.5-flash")
