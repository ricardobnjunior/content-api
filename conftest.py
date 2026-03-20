"""Root conftest.py for test configuration."""

import os
import sys

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

# Set required environment variables before any app imports
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_conftest.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")
