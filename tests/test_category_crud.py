"""Unit tests for Category CRUD operations using a real in-memory SQLite DB."""

import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_crud.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.crud.category import (  # noqa: E402
    _generate_slug,
    create_category,
    delete_category,
    get_categories,
    get_category,
    update_category,
)
from app.schemas.category import CategoryCreate, CategoryUpdate  # noqa: E402


# ---------------------------------------------------------------------------
# Slug generation tests (pure function, no DB needed)
# ---------------------------------------------------------------------------

class TestGenerateSlug:
    """Tests for the _generate_slug helper."""

    def test_simple_name(self) -> None:
        assert _generate_slug("Technology") == "technology"

    def test_multi_word_name(self) -> None:
        assert _generate_slug("Hello World") == "hello-world"

    def test_special_characters_replaced(self) -> None:
        assert _generate_slug("Tech & Science!") == "tech-science"

    def test_unicode_accent_normalized(self) -> None:
        assert _generate_slug("Café") == "cafe"

    def test_leading_trailing_hyphens_stripped(self) -> None:
        slug = _generate_slug("!leading and trailing!")
        assert not slug.startswith("-")
        assert not slug.endswith("-")

    def test_numbers_preserved(self) -> None:
        assert _generate_slug("Top 10 Tips") == "top-10-tips"

    def test_already_lowercase(self) -> None:
        assert _generate_slug("already") == "already"

    def test_multiple_spaces_become_single_hyphen(self) -> None:
        assert _generate_slug("a  b") == "a-b"


# ---------------------------------------------------------------------------
# CRUD tests using db_session fixture from conftest.py
# ---------------------------------------------------------------------------

class TestCreateCategoryCRUD:
    """Tests for create_category()."""

    def test_create_returns_category_with_id(self, db_session) -> None:
        data = CategoryCreate(name="CRUD Test", description="desc")
        cat = create_category(db_session, data)
        assert cat.id is not None
        assert cat.name == "CRUD Test"
        assert cat.slug == "crud-test"
        assert cat.description == "desc"

    def test_create_generates_slug(self, db_session) -> None:
        data = CategoryCreate(name="Slug From Name")
        cat = create_category(db_session, data)
        assert cat.slug == "slug-from-name"

    def test_create_without_description(self, db_session) -> None:
        data = CategoryCreate(name="No Desc Cat")
        cat = create_category(db_session, data)
        assert cat.description is None


class TestGetCategoryCRUD:
    """Tests for get_category()."""

    def test_get_existing_category(self, db_session) -> None:
        created = create_category(db_session, CategoryCreate(name="GetMe"))
        fetched = get_category(db_session, created.id)
        assert fetched is not None
        assert fetched.id == created.id

    def test_get_nonexistent_returns_none(self, db_session) -> None:
        result = get_category(db_session, 99999)
        assert result is None


class TestGetCategoriesCRUD:
    """Tests for get_categories()."""

    def test_returns_all_categories(self, db_session) -> None:
        create_category(db_session, CategoryCreate(name="CatList1"))
        create_category(db_session, CategoryCreate(name="CatList2"))
        cats = get_categories(db_session)
        names = [c.name for c in cats]
        assert "CatList1" in names
        assert "CatList2" in names

    def test_skip_and_limit(self, db_session) -> None:
        for i in range(5):
            create_category(db_session, CategoryCreate(name=f"LimitCat{i}"))
        cats = get_categories(db_session, skip=1, limit=2)
        assert len(cats) == 2

    def test_empty_db_returns_empty_list(self, db_session) -> None:
        cats = get_categories(db_session)
        assert cats == []


class TestUpdateCategoryCRUD:
    """Tests for update_category()."""

    def test_update_name_changes_slug(self, db_session) -> None:
        created = create_category(db_session, CategoryCreate(name="Before Update"))
        updated = update_category(
            db_session, created.id, CategoryUpdate(name="After Update")
        )
        assert updated is not None
        assert updated.name == "After Update"
        assert updated.slug == "after-update"

    def test_update_description_only(self, db_session) -> None:
        created = create_category(db_session, CategoryCreate(name="Desc Update Cat"))
        updated = update_category(
            db_session, created.id, CategoryUpdate(description="New desc")
        )
        assert updated is not None
        assert updated.description == "New desc"
        assert updated.name == "Desc Update Cat"

    def test_update_nonexistent_returns_none(self, db_session) -> None:
        result = update_category(db_session, 99999, CategoryUpdate(name="X"))
        assert result is None

    def test_update_with_no_fields_leaves_unchanged(self, db_session) -> None:
        created = create_category(
            db_session, CategoryCreate(name="Unchanged Cat", description="original")
        )
        updated = update_category(db_session, created.id, CategoryUpdate())
        assert updated is not None
        assert updated.name == "Unchanged Cat"
        assert updated.description == "original"


class TestDeleteCategoryCRUD:
    """Tests for delete_category()."""

    def test_delete_existing_returns_true(self, db_session) -> None:
        created = create_category(db_session, CategoryCreate(name="DeleteMe"))
        result = delete_category(db_session, created.id)
        assert result is True

    def test_deleted_category_no_longer_exists(self, db_session) -> None:
        created = create_category(db_session, CategoryCreate(name="GoneForever"))
        delete_category(db_session, created.id)
        assert get_category(db_session, created.id) is None

    def test_delete_nonexistent_returns_false(self, db_session) -> None:
        result = delete_category(db_session, 99999)
        assert result is False
