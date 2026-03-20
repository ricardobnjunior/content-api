"""Main API router aggregating all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints.stats import router as stats_router

router = APIRouter(prefix="/api/v1")

router.include_router(articles.router, prefix="/articles", tags=["articles"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
router.include_router(stats_router, prefix="/stats", tags=["stats"])
