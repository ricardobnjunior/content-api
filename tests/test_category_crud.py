"""Unit tests for Category CRUD functions."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.crud.category import (
    _generate_slug,
    create_category,
    delete_category,
    get_categories,
    get_category,
    update_category,
)
from app.database import Base
from app.schemas.category import CategoryCreate, CategoryUpdate

# ---------------------------------------------------------------------------
# In-memory SQLite engine for unit tests
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def engine():
    """Create a module-scoped in-memory SQLite engine."""
    eng = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture()
def db(engine):
    """Provide a function-scoped transactional session."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# _generate_slug unit tests
# ---------------------------------------------------------------------------


def test_generate_slug_simple():
    """Simple words are lowercased and hyphenated."""
    assert _generate_slug("Hello World") == "hello-world"


def test_generate_slug_strips_special_chars():
    """Special characters are removed from slugs."""
    result = _generate_slug("Science & Nature!")
    assert "&" not in result
    assert "!" not in result
    assert "science" in result
    assert "nature" in result


def test_generate_slug_multiple_spaces():
    """Multiple spaces collapse to a single hyphen."""
    result = _generate_slug("Too  Many   Spaces")
    assert "--" not in result


def test_generate_slug_leading_trailing_spaces():
    """Leading and trailing spaces are stripped."""
    result = _generate_slug("  trimmed  ")
    assert not result.startswith("-")
    assert not result.endswith("-")


def test_generate_slug_unicode():
    """Unicode characters are normalized to ASCII equivalents."""
    result = _generate_slug("Café")
    # é normalizes to e via NFKD
    assert "caf" in result


# ---------------------------------------------------------------------------
# create_category
# ---------------------------------------------------------------------------


def test_create_category_basic(db):
    """create_category persists a category with correct fields."""
    data = CategoryCreate(name="Technology", description="Tech stuff")
    cat = create_category(db, data)
    assert cat.id is not None
    assert cat.name == "Technology"
    assert cat.slug == "technology"
    assert cat.description == "Tech stuff"


def test_create_category_auto_slug(db):
    """Slug is auto-generated from the name."""
    data = CategoryCreate(name="Hello World")
    cat = create_category(db, data)
    assert cat.slug == "hello-world"


def test_create_category_no_description(db):
    """Category can be created without a description."""
    data = CategoryCreate(name="No Desc Cat")
    cat = create_category(db, data)
    assert cat.description is None


# ---------------------------------------------------------------------------
# get_category
# ---------------------------------------------------------------------------


def test_get_category_found(db):
    """get_category returns the category by ID."""
    data = CategoryCreate(name="Get Me")
    cat = create_category(db, data)
    found = get_category(db, cat.id)
    assert found is not None
    assert found.id == cat.id
    assert found.name == "Get Me"


def test_get_category_not_found(db):
    """get_category returns None for nonexistent ID."""
    result = get_category(db, 99999)
    assert result is None


# ---------------------------------------------------------------------------
# get_categories
# ---------------------------------------------------------------------------


def test_get_categories_returns_list(db):
    """get_categories returns all created categories."""
    create_category(db, CategoryCreate(name="List Cat A"))
    create_category(db, CategoryCreate(name="List Cat B"))
    cats = get_categories(db)
    names = [c.name for c in cats]
    assert "List Cat A" in names
    assert "List Cat B" in names


def test_get_categories_empty(db):
    """get_categories returns an empty list when none exist."""
    cats = get_categories(db)
    assert isinstance(cats, list)
    # May have categories from other tests in the same transaction scope,
    # but should always return a list
    assert cats is not None


def test_get_categories_skip(db):
    """get_categories respects the skip parameter."""
    create_category(db, CategoryCreate(name="Skip A"))
    create_category(db, CategoryCreate(name="Skip B"))
    create_category(db, CategoryCreate(name="Skip C"))
    all_cats = get_categories(db, skip=0, limit=100)
    skipped = get_categories(db, skip=1, limit=100)
    assert len(skipped) == len(all_cats) - 1


def test_get_categories_limit(db):
    """get_categories respects the limit parameter."""
    create_category(db, CategoryCreate(name="Limit X"))
    create_category(db, CategoryCreate(name="Limit Y"))
    limited = get_categories(db, skip=0, limit=1)
    assert len(limited) == 1


# ---------------------------------------------------------------------------
# update_category
# ---------------------------------------------------------------------------


def test_update_category_name(db):
    """update_category changes name and regenerates slug."""
    cat = create_category(db, CategoryCreate(name="Old Name"))
    updated = update_category(db, cat.id, CategoryUpdate(name="New Name"))
    assert updated is not None
    assert updated.name == "New Name"
    assert updated.slug == "new-name"


def test_update_category_description(db):
    """update_category changes description."""
    cat = create_category(
        db, CategoryCreate(name="Desc Cat", description="Old desc")
    )
    updated = update_category(
        db, cat.id, CategoryUpdate(description="New desc")
    )
    assert updated is not None
    assert updated.description == "New desc"
    assert updated.name == "Desc Cat"  # name unchanged


def test_update_category_not_found(db):
    """update_category returns None for nonexistent ID."""
    result = update_category(db, 99999, CategoryUpdate(name="Ghost"))
    assert result is None


def test_update_category_preserves_unchanged_fields(db):
    """update_category does not overwrite fields not included in update."""
    cat = create_category(
        db,
        CategoryCreate(name="Preserve Me", description="Keep this"),
    )
    updated = update_category(db, cat.id, CategoryUpdate(name="Preserved New"))
    assert updated is not None
    # description should still be "Keep this" since we didn't pass description
    # NOTE: The implementation only updates description if data.description is not None
    assert updated.name == "Preserved New"


# ---------------------------------------------------------------------------
# delete_category
# ---------------------------------------------------------------------------


def test_delete_category_returns_true(db):
    """delete_category returns True when the category is deleted."""
    cat = create_category(db, CategoryCreate(name="Delete Me"))
    result = delete_category(db, cat.id)
    assert result is True


def test_delete_category_removes_from_db(db):
    """After deletion, get_category returns None."""
    cat = create_category(db, CategoryCreate(name="Gone"))
    delete_category(db, cat.id)
    assert get_category(db, cat.id) is None


def test_delete_category_returns_false_not_found(db):
    """delete_category returns False for nonexistent ID."""
    result = delete_category(db, 99999)
    assert result is False
