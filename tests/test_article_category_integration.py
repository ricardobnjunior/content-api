"""Integration tests for article-category many-to-many relationship via CRUD."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.crud.article import create_article, get_article, update_article
from app.crud.category import create_category
from app.database import Base
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.schemas.category import CategoryCreate

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def engine():
    """Create a module-scoped in-memory SQLite engine with all tables."""
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
# Article creation with categories
# ---------------------------------------------------------------------------


def test_create_article_with_single_category(db):
    """create_article assigns a single category when category_ids provided."""
    cat = create_category(db, CategoryCreate(name="Tech"))
    data = ArticleCreate(
        title="Tech Article",
        body="Body",
        author="Author",
        category_ids=[cat.id],
    )
    article = create_article(db, data)
    assert article.id is not None
    assert len(article.categories) == 1
    assert article.categories[0].id == cat.id


def test_create_article_with_multiple_categories(db):
    """create_article assigns multiple categories."""
    cat1 = create_category(db, CategoryCreate(name="Cat A"))
    cat2 = create_category(db, CategoryCreate(name="Cat B"))
    data = ArticleCreate(
        title="Multi Cat",
        body="Body",
        author="Author",
        category_ids=[cat1.id, cat2.id],
    )
    article = create_article(db, data)
    assigned_ids = {c.id for c in article.categories}
    assert cat1.id in assigned_ids
    assert cat2.id in assigned_ids


def test_create_article_without_category_ids(db):
    """create_article with no category_ids results in empty categories."""
    data = ArticleCreate(
        title="No Category",
        body="Body",
        author="Author",
    )
    article = create_article(db, data)
    assert article.categories == []


def test_create_article_with_nonexistent_category_ids(db):
    """Nonexistent category IDs are silently ignored."""
    data = ArticleCreate(
        title="Ghost Cat Article",
        body="Body",
        author="Author",
        category_ids=[99999, 88888],
    )
    article = create_article(db, data)
    assert article.categories == []


def test_create_article_with_empty_category_ids(db):
    """Explicit empty list produces no categories."""
    data = ArticleCreate(
        title="Empty IDs",
        body="Body",
        author="Author",
        category_ids=[],
    )
    article = create_article(db, data)
    assert article.categories == []


# ---------------------------------------------------------------------------
# get_article with categories
# ---------------------------------------------------------------------------


def test_get_article_includes_categories(db):
    """get_article returns article with its categories loaded."""
    cat = create_category(db, CategoryCreate(name="Loadable"))
    created = create_article(
        db,
        ArticleCreate(
            title="With Cat",
            body="Body",
            author="Author",
            category_ids=[cat.id],
        ),
    )
    fetched = get_article(db, created.id)
    assert fetched is not None
    assert len(fetched.categories) == 1
    assert fetched.categories[0].name == "Loadable"


# ---------------------------------------------------------------------------
# update_article with categories
# ---------------------------------------------------------------------------


def test_update_article_adds_categories(db):
    """update_article can add categories to an article that had none."""
    cat = create_category(db, CategoryCreate(name="Added Later"))
    article = create_article(
        db,
        ArticleCreate(title="No Cats Initially", body="Body", author="Auth"),
    )
    assert article.categories == []

    updated = update_article(
        db,
        article.id,
        ArticleUpdate(category_ids=[cat.id]),
    )
    assert updated is not None
    assert len(updated.categories) == 1
    assert updated.categories[0].id == cat.id


def test_update_article_replaces_categories(db):
    """update_article replaces existing categories with new ones."""
    cat1 = create_category(db, CategoryCreate(name="Old Cat"))
    cat2 = create_category(db, CategoryCreate(name="New Cat"))

    article = create_article(
        db,
        ArticleCreate(
            title="Replace Cats",
            body="Body",
            author="Auth",
            category_ids=[cat1.id],
        ),
    )
    assert len(article.categories) == 1

    updated = update_article(
        db,
        article.id,
        ArticleUpdate(category_ids=[cat2.id]),
    )
    assert updated is not None
    assert len(updated.categories) == 1
    assert updated.categories[0].id == cat2.id


def test_update_article_clears_categories_with_empty_list(db):
    """update_article with empty category_ids clears all categories."""
    cat = create_category(db, CategoryCreate(name="Clear Me"))
    article = create_article(
        db,
        ArticleCreate(
            title="Has Cat",
            body="Body",
            author="Auth",
            category_ids=[cat.id],
        ),
    )
    assert len(article.categories) == 1

    updated = update_article(
        db,
        article.id,
        ArticleUpdate(category_ids=[]),
    )
    assert updated is not None
    assert updated.categories == []


def test_update_article_not_found_returns_none(db):
    """update_article returns None for a nonexistent article."""
    result = update_article(db, 99999, ArticleUpdate(title="Ghost"))
    assert result is None


def test_update_article_preserves_existing_fields(db):
    """update_article with only category_ids preserves other article fields."""
    cat = create_category(db, CategoryCreate(name="Preserve Field Cat"))
    article = create_article(
        db,
        ArticleCreate(
            title="Keep This Title",
            body="Keep This Body",
            author="Keep This Author",
        ),
    )
    updated = update_article(
        db,
        article.id,
        ArticleUpdate(category_ids=[cat.id]),
    )
    assert updated is not None
    assert updated.title == "Keep This Title"
    assert updated.body == "Keep This Body"
    assert updated.author == "Keep This Author"
