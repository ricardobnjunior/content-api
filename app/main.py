"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="Blog API")

app.include_router(api_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
