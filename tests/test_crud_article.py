"""Unit tests for Article CRUD functions."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.crud.article import (
    create_article,
    delete_article,
    get_article,
    get_articles,
    update_article,
)
from app.database import Base
from app.models.article import ArticleStatus
from app.schemas.article import ArticleCreate, ArticleUpdate

TEST_DATABASE_URL = "sqlite:///./test_crud.db"


@pytest.fixture()
def db():
    """Provide a fresh in-memory SQLite session for each test."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _make_create_data(**kwargs) -> ArticleCreate:
    """Helper to build an ArticleCreate with sensible defaults."""
    defaults = {
        "title": "Default Title",
        "body": "Default body content.",
        "author": "Default Author",
        "status": ArticleStatus.draft,
    }
    defaults.update(kwargs)
    return ArticleCreate(**defaults)


# ---------------------------------------------------------------------------
# create_article
# ---------------------------------------------------------------------------

def test_create_article_returns_article(db):
    """create_article persists and returns an Article with an ID."""
    data = _make_create_data()
    article = create_article(db, data)
    assert article.id is not None
    assert article.title == "Default Title"
    assert article.body == "Default body content."
    assert article.author == "Default Author"
    assert article.status == ArticleStatus.draft


def test_create_article_with_published_status(db):
    """create_article stores the published status correctly."""
    data = _make_create_data(status=ArticleStatus.published)
    article = create_article(db, data)
    assert article.status == ArticleStatus.published


def test_create_article_increments_id(db):
    """Two articles get distinct auto-incremented IDs."""
    a1 = create_article(db, _make_create_data(title="First"))
    a2 = create_article(db, _make_create_data(title="Second"))
    assert a1.id != a2.id


# ---------------------------------------------------------------------------
# get_article
# ---------------------------------------------------------------------------

def test_get_article_found(db):
    """get_article returns the correct article by ID."""
    created = create_article(db, _make_create_data())
    fetched = get_article(db, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == created.title


def test_get_article_not_found(db):
    """get_article returns None for a non-existent ID."""
    result = get_article(db, 999999)
    assert result is None


def test_get_article_returns_none_for_zero_id(db):
    """get_article returns None when article_id is 0 (no such record)."""
    result = get_article(db, 0)
    assert result is None


# ---------------------------------------------------------------------------
# get_articles
# ---------------------------------------------------------------------------

def test_get_articles_empty(db):
    """get_articles returns empty list and zero total when no articles exist."""
    items, total = get_articles(db)
    assert items == []
    assert total == 0


def test_get_articles_returns_all(db):
    """get_articles returns all articles and correct total."""
    for i in range(3):
        create_article(db, _make_create_data(title=f"Article {i}"))
    items, total = get_articles(db)
    assert total == 3
    assert len(items) == 3


def test_get_articles_pagination_skip(db):
    """get_articles with skip omits the first N records."""
    for i in range(5):
        create_article(db, _make_create_data(title=f"Article {i}"))
    items, total = get_articles(db, skip=3, limit=10)
    assert total == 5
    assert len(items) == 2


def test_get_articles_pagination_limit(db):
    """get_articles with limit caps the returned results."""
    for i in range(5):
        create_article(db, _make_create_data(title=f"Article {i}"))
    items, total = get_articles(db, skip=0, limit=2)
    assert total == 5
    assert len(items) == 2


def test_get_articles_skip_beyond_total(db):
    """get_articles returns empty list when skip exceeds total."""
    for i in range(3):
        create_article(db, _make_create_data(title=f"Article {i}"))
    items, total = get_articles(db, skip=100, limit=10)
    assert total == 3
    assert len(items) == 0


# ---------------------------------------------------------------------------
# update_article
# ---------------------------------------------------------------------------

def test_update_article_title(db):
    """update_article changes the title and leaves other fields intact."""
    created = create_article(db, _make_create_data())
    update_data = ArticleUpdate(title="New Title")
    updated = update_article(db, created.id, update_data)
    assert updated is not None
    assert updated.title == "New Title"
    assert updated.body == created.body
    assert updated.author == created.author


def test_update_article_status(db):
    """update_article changes status from draft to published."""
    created = create_article(db, _make_create_data())
    update_data = ArticleUpdate(status=ArticleStatus.published)
    updated = update_article(db, created.id, update_data)
    assert updated is not None
    assert updated.status == ArticleStatus.published


def test_update_article_all_fields(db):
    """update_article can update all fields at once."""
    created = create_article(db, _make_create_data())
    update_data = ArticleUpdate(
        title="New Title",
        body="New body",
        author="New Author",
        status=ArticleStatus.published,
    )
    updated = update_article(db, created.id, update_data)
    assert updated.title == "New Title"
    assert updated.body == "New body"
    assert updated.author == "New Author"
    assert updated.status == ArticleStatus.published


def test_update_article_not_found(db):
    """update_article returns None for a non-existent article ID."""
    update_data = ArticleUpdate(title="Won't be set")
    result = update_article(db, 999999, update_data)
    assert result is None


def test_update_article_empty_update(db):
    """update_article with no fields set leaves article unchanged."""
    created = create_article(db, _make_create_data())
    update_data = ArticleUpdate()
    updated = update_article(db, created.id, update_data)
    assert updated is not None
    assert updated.title == created.title
    assert updated.body == created.body
    assert updated.author == created.author
    assert updated.status == created.status


# ---------------------------------------------------------------------------
# delete_article
# ---------------------------------------------------------------------------

def test_delete_article_returns_true(db):
    """delete_article returns True when the article exists and is deleted."""
    created = create_article(db, _make_create_data())
    result = delete_article(db, created.id)
    assert result is True


def test_delete_article_removes_from_db(db):
    """After delete_article, get_article returns None for that ID."""
    created = create_article(db, _make_create_data())
    delete_article(db, created.id)
    assert get_article(db, created.id) is None


def test_delete_article_not_found(db):
    """delete_article returns False for a non-existent article ID."""
    result = delete_article(db, 999999)
    assert result is False


def test_delete_article_does_not_affect_others(db):
    """Deleting one article leaves others untouched."""
    a1 = create_article(db, _make_create_data(title="Keep me"))
    a2 = create_article(db, _make_create_data(title="Delete me"))
    delete_article(db, a2.id)
    assert get_article(db, a1.id) is not None
    assert get_article(db, a2.id) is None
