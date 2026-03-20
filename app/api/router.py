"""Main API router aggregating all endpoint sub-routers."""

from fastapi import APIRouter


router = APIRouter(prefix="/api/v1")

router.include_router(articles.router)
router.include_router(categories.router)
router.include_router(suggestions.router)
