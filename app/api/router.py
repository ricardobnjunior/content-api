"""Main API router that aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints import articles, categories, stats, suggestions
from app.api.endpoints.export import router as export_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(articles.router)
api_router.include_router(categories.router)
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(suggestions.router)
api_router.include_router(export_router)
