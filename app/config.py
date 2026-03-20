"""Application configuration using Pydantic Settings."""

import json
import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        database_url: SQLAlchemy database connection string.
        secret_key: Secret key for JWT token signing.
        environment: Deployment environment (development/production).
        upload_dir: Directory for storing uploaded files.
    """

    database_url: str = "sqlite:///./articles.db"
    secret_key: str = "dev-secret-key-change-in-production"
    environment: str = "development"
    upload_dir: str = "uploads"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    Returns:
        Settings instance with values loaded from environment.
    """
    return Settings()
