"""Root conftest for test configuration."""

import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

# Set required environment variables before any app imports
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_recommendations.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("OPENROUTER_API_KEY", "test-api-key")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")
