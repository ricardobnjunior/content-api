"""Tests for Category and Article Pydantic schemas."""

import pytest

from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.article import ArticleCreate, ArticleResponse, ArticleUpdate
from app.models.article import ArticleStatus


class TestCategoryCreate:
    """Tests for CategoryCreate schema."""

    def test_valid_name_only(self) -> None:
        schema = CategoryCreate(name="Tech")
        assert schema.name == "Tech"
        assert schema.description is None

    def test_valid_name_and_description(self) -> None:
        schema = CategoryCreate(name="Science", description="About science")
        assert schema.description == "About science"

    def test_name_too_long_raises_validation_error(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CategoryCreate(name="x" * 101)

    def test_name_exactly_100_chars_is_valid(self) -> None:
        schema = CategoryCreate(name="x" * 100)
        assert len(schema.name) == 100

    def test_missing_name_raises_validation_error(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CategoryCreate()  # type: ignore


class TestCategoryUpdate:
    """Tests for CategoryUpdate schema."""

    def test_all_fields_optional(self) -> None:
        schema = CategoryUpdate()
        assert schema.name is None
        assert schema.description is None

    def test_partial_update_name_only(self) -> None:
        schema = CategoryUpdate(name="New Name")
        assert schema.name == "New Name"
        assert schema.description is None

    def test_partial_update_description_only(self) -> None:
        schema = CategoryUpdate(description="New desc")
        assert schema.name is None
        assert schema.description == "New desc"

    def test_name_max_length_enforced(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CategoryUpdate(name="y" * 101)


class TestCategoryResponse:
    """Tests for CategoryResponse schema."""

    def test_from_dict(self) -> None:
        schema = CategoryResponse(id=1, name="Test", slug="test", description=None)
        assert schema.id == 1
        assert schema.slug == "test"

    def test_description_optional(self) -> None:
        schema = CategoryResponse(id=2, name="Test2", slug="test2")
        assert schema.description is None


class TestArticleCreateWithCategories:
    """Tests for ArticleCreate with category_ids."""

    def test_default_category_ids_is_empty(self) -> None:
        schema = ArticleCreate(title="T", body="B", author="A")
        assert schema.category_ids == []

    def test_category_ids_accepted(self) -> None:
        schema = ArticleCreate(title="T", body="B", author="A", category_ids=[1, 2, 3])
        assert schema.category_ids == [1, 2, 3]

    def test_default_status_is_draft(self) -> None:
        schema = ArticleCreate(title="T", body="B", author="A")
        assert schema.status == ArticleStatus.DRAFT


class TestArticleUpdateWithCategories:
    """Tests for ArticleUpdate with category_ids."""

    def test_default_category_ids_is_empty(self) -> None:
        schema = ArticleUpdate()
        assert schema.category_ids == []

    def test_category_ids_can_be_set(self) -> None:
        schema = ArticleUpdate(category_ids=[5, 6])
        assert schema.category_ids == [5, 6]

    def test_all_fields_optional(self) -> None:
        schema = ArticleUpdate()
        assert schema.title is None
        assert schema.body is None
        assert schema.author is None
        assert schema.status is None
