"""Main API router that aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints import articles, categories, stats
from app.api.endpoints.export import router as export_router

router = APIRouter(prefix="/api/v1")

router.include_router(articles.router)
router.include_router(categories.router)
router.include_router(stats.router)
router.include_router(export_router)
