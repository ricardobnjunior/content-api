"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - create tables on startup."""
    # Tables are created by tests via fixtures; skip in test mode
    import os
    if os.environ.get("TESTING") != "1":
        from app.database import create_tables
        create_tables()
    yield


app = FastAPI(title="Articles API", lifespan=lifespan)

app.include_router(api_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
