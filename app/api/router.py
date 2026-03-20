"""Main API router that aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints import articles, categories, recommendations, suggestions

router = APIRouter()

router.include_router(articles.router, prefix="/articles", tags=["articles"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
router.include_router(suggestions.router, prefix="/suggestions", tags=["suggestions"])
router.include_router(
    recommendations.router, prefix="/recommendations", tags=["recommendations"]
)
