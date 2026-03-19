"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.router import api_router
from app.config import settings
from app.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events.

    Args:
        app: The FastAPI application instance.

    Yields:
        None
    """
    create_tables()
    yield


app = FastAPI(title="Content API", lifespan=lifespan)

app.include_router(api_router)


@app.get("/health")
def health_check() -> dict:
    """Return the health status of the application.

    Returns:
        A dictionary with the application status and current environment.
    """
    return {"status": "ok", "environment": settings.environment}
