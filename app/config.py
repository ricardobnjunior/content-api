"""Application configuration."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    database_url: str = os.environ.get("DATABASE_URL", "sqlite:///./app.db")
    secret_key: str = os.environ.get("SECRET_KEY", "default-secret-key")

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
