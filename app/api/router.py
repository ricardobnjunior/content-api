"""Central API router."""

from fastapi import APIRouter

from app.api.endpoints.articles import router as articles_router
from app.api.endpoints.categories import router as categories_router

router = APIRouter(prefix="/api/v1")
router.include_router(articles_router, prefix="/articles", tags=["articles"])
router.include_router(categories_router, prefix="/categories", tags=["categories"])
