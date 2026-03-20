"""Models package — imports all ORM models so create_tables() discovers them."""

from app.models.article import Article, ArticleStatus

__all__ = ["Article", "ArticleStatus"]
