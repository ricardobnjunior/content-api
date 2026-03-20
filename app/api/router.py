"""Main API router combining all endpoint sub-routers."""

from fastapi import APIRouter

from app.api.endpoints import articles, categories, stats

router = APIRouter(prefix="/api/v1")

router.include_router(articles.router, prefix="/articles", tags=["articles"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
router.include_router(stats.router, prefix="/stats", tags=["stats"])
