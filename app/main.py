"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import router

app = FastAPI(title="Articles API")

app.include_router(router)
