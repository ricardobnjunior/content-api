"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import Base, engine


def create_tables() -> None:
    """Create all database tables defined in ORM models."""
    Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    application = FastAPI(
        title="Articles API",
        description="REST API for managing articles",
        version="1.0.0",
    )

    create_tables()

    os.makedirs(settings.upload_dir, exist_ok=True)
    application.mount(
        "/uploads",
        StaticFiles(directory=settings.upload_dir),
        name="uploads",
    )

    from app.api.router import router

    application.include_router(router)

    @application.get("/health")
    def health_check() -> dict:
        """Health check endpoint.

        Returns:
            Dictionary with status field.
        """
        return {"status": "ok"}

    return application


app = create_app()
