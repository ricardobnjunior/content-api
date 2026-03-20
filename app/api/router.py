"""Main API router that aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints import articles, categories, export, stats

router = APIRouter()

router.include_router(articles.router, prefix="/articles", tags=["articles"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
router.include_router(stats.router, prefix="/stats", tags=["stats"])
router.include_router(export.router, prefix="/export", tags=["export"])
