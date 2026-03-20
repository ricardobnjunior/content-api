"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings
from app.database import create_tables


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan events.

    Creates database tables on startup.

    Args:
        application: The FastAPI application instance.

    Yields:
        None
    """
    create_tables()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    application = FastAPI(
        title="Content API",
        lifespan=lifespan,
    )

    application.include_router(api_router)

    @application.get("/health", tags=["health"])
    def health_check() -> dict:
        """Return service health status.

        Returns:
            A dict with status and current environment name.
        """
        return {"status": "ok", "environment": settings.environment}

    return application


app = create_app()
