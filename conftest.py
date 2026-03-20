"""Root conftest.py — configures sys.path and shared fixtures."""

import sys
import os

# Ensure the project root is on sys.path so `from app.xxx import ...` works.
sys.path.insert(0, os.path.dirname(__file__))
