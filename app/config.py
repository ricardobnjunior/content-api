"""Application configuration via pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file.

    Attributes:
        database_url: SQLAlchemy database connection URL.
        secret_key: Secret key for cryptographic operations.
        environment: Deployment environment name.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    database_url: str = "sqlite:///content.db"
    secret_key: str = "dev-secret-change-in-production"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance.

    Returns:
        The singleton Settings instance.
    """
    return Settings()
