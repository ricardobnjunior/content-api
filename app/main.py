"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="Article API", version="1.0.0")

app.include_router(api_router)


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint.

    Returns:
        A dictionary with status information.
    """
    return {"status": "ok"}
