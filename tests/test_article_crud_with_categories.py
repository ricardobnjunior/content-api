"""Tests for Article CRUD with category relationships."""

import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_article_cat.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.crud.article import (  # noqa: E402
    create_article,
    delete_article,
    get_article,
    update_article,
)
from app.crud.category import create_category  # noqa: E402
from app.schemas.article import ArticleCreate, ArticleUpdate  # noqa: E402
from app.schemas.category import CategoryCreate  # noqa: E402


class TestCreateArticleWithCategories:
    """Tests for create_article() with category_ids."""

    def test_create_article_no_categories(self, db_session) -> None:
        data = ArticleCreate(title="T", body="B", author="A")
        article = create_article(db_session, data)
        assert article.id is not None
        assert article.categories == []

    def test_create_article_with_valid_category(self, db_session) -> None:
        cat = create_category(db_session, CategoryCreate(name="ValidCat"))
        data = ArticleCreate(
            title="With Cat", body="B", author="A", category_ids=[cat.id]
        )
        article = create_article(db_session, data)
        assert len(article.categories) == 1
        assert article.categories[0].id == cat.id

    def test_create_article_with_multiple_categories(self, db_session) -> None:
        cat1 = create_category(db_session, CategoryCreate(name="CatX"))
        cat2 = create_category(db_session, CategoryCreate(name="CatY"))
        data = ArticleCreate(
            title="Multi", body="B", author="A", category_ids=[cat1.id, cat2.id]
        )
        article = create_article(db_session, data)
        assert len(article.categories) == 2

    def test_create_article_with_nonexistent_category_id_ignored(
        self, db_session
    ) -> None:
        data = ArticleCreate(
            title="Ghost Cat", body="B", author="A", category_ids=[99999]
        )
        article = create_article(db_session, data)
        assert article.categories == []

    def test_create_article_with_empty_category_ids(self, db_session) -> None:
        data = ArticleCreate(title="Empty", body="B", author="A", category_ids=[])
        article = create_article(db_session, data)
        assert article.categories == []


class TestUpdateArticleWithCategories:
    """Tests for update_article() with category_ids."""

    def test_update_article_adds_categories(self, db_session) -> None:
        cat = create_category(db_session, CategoryCreate(name="AddCat"))
        article = create_article(
            db_session, ArticleCreate(title="NoC", body="B", author="A")
        )
        updated = update_article(
            db_session, article.id, ArticleUpdate(category_ids=[cat.id])
        )
        assert updated is not None
        assert len(updated.categories) == 1
        assert updated.categories[0].id == cat.id

    def test_update_article_replaces_categories(self, db_session) -> None:
        cat1 = create_category(db_session, CategoryCreate(name="ReplaceCatA"))
        cat2 = create_category(db_session, CategoryCreate(name="ReplaceCatB"))
        article = create_article(
            db_session,
            ArticleCreate(title="Orig", body="B", author="A", category_ids=[cat1.id]),
        )
        updated = update_article(
            db_session, article.id, ArticleUpdate(category_ids=[cat2.id])
        )
        assert updated is not None
        assert len(updated.categories) == 1
        assert updated.categories[0].id == cat2.id

    def test_update_article_clears_categories_with_empty_list(
        self, db_session
    ) -> None:
        cat = create_category(db_session, CategoryCreate(name="ClearCatCRUD"))
        article = create_article(
            db_session,
            ArticleCreate(title="HasCat", body="B", author="A", category_ids=[cat.id]),
        )
        updated = update_article(
            db_session, article.id, ArticleUpdate(category_ids=[])
        )
        assert updated is not None
        assert updated.categories == []

    def test_update_nonexistent_article_returns_none(self, db_session) -> None:
        result = update_article(db_session, 99999, ArticleUpdate(title="X"))
        assert result is None

    def test_update_other_fields_alongside_categories(self, db_session) -> None:
        cat = create_category(db_session, CategoryCreate(name="SideEffect"))
        article = create_article(
            db_session, ArticleCreate(title="Orig Title", body="B", author="A")
        )
        updated = update_article(
            db_session,
            article.id,
            ArticleUpdate(title="New Title", category_ids=[cat.id]),
        )
        assert updated is not None
        assert updated.title == "New Title"
        assert len(updated.categories) == 1


class TestDeleteArticleWithCategories:
    """Tests for delete_article() when categories are present."""

    def test_delete_article_with_category_succeeds(self, db_session) -> None:
        cat = create_category(db_session, CategoryCreate(name="DelCat"))
        article = create_article(
            db_session,
            ArticleCreate(title="Del", body="B", author="A", category_ids=[cat.id]),
        )
        result = delete_article(db_session, article.id)
        assert result is True
        assert get_article(db_session, article.id) is None

    def test_delete_article_leaves_category_intact(self, db_session) -> None:
        from app.crud.category import get_category  # noqa: E402

        cat = create_category(db_session, CategoryCreate(name="LeftAlone"))
        article = create_article(
            db_session,
            ArticleCreate(title="Gone", body="B", author="A", category_ids=[cat.id]),
        )
        delete_article(db_session, article.id)
        surviving_cat = get_category(db_session, cat.id)
        assert surviving_cat is not None
        assert surviving_cat.name == "LeftAlone"
