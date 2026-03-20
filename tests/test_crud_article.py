"""Unit tests for CRUD functions in app/crud/article.py."""

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
from app.models.article import ArticleStatus
from app.schemas.article import ArticleCreate, ArticleUpdate

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db():
    """Provide a fresh in-memory SQLite session per test."""
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    import app.models  # noqa: F401 — ensures models are registered with Base

    from app.database import Base
    Base.metadata.create_all(engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def sample_create_data() -> ArticleCreate:
    """Return a valid ArticleCreate schema instance."""
    return ArticleCreate(
        title="Unit Test Article",
        body="Body content for unit test.",
        author="Unit Tester",
        status=ArticleStatus.draft,
    )


# ---------------------------------------------------------------------------
# create_article
# ---------------------------------------------------------------------------


def test_create_article_returns_article(db, sample_create_data):
    """create_article persists and returns an Article with an assigned ID."""
    article = create_article(db, sample_create_data)
    assert article.id is not None
    assert article.id > 0
    assert article.title == sample_create_data.title
    assert article.body == sample_create_data.body
    assert article.author == sample_create_data.author
    assert article.status == ArticleStatus.draft


def test_create_article_default_status(db):
    """create_article with explicit draft status stores draft."""
    data = ArticleCreate(
        title="Draft Article",
        body="Some body",
        author="Author",
        status=ArticleStatus.draft,
    )
    article = create_article(db, data)
    assert article.status == ArticleStatus.draft


def test_create_article_published_status(db):
    """create_article with published status stores published."""
    data = ArticleCreate(
        title="Published Article",
        body="Some body",
        author="Author",
        status=ArticleStatus.published,
    )
    article = create_article(db, data)
    assert article.status == ArticleStatus.published


def test_create_multiple_articles_have_unique_ids(db, sample_create_data):
    """Two articles created sequentially get different IDs."""
    a1 = create_article(db, sample_create_data)
    a2 = create_article(db, sample_create_data)
    assert a1.id != a2.id


# ---------------------------------------------------------------------------
# get_article
# ---------------------------------------------------------------------------


def test_get_article_returns_correct_article(db, sample_create_data):
    """get_article returns the article matching the given ID."""
    created = create_article(db, sample_create_data)
    fetched = get_article(db, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == created.title


def test_get_article_nonexistent_returns_none(db):
    """get_article returns None for a non-existent ID."""
    result = get_article(db, 99999)
    assert result is None


def test_get_article_wrong_id_returns_none(db, sample_create_data):
    """get_article with wrong ID returns None, not another article."""
    create_article(db, sample_create_data)
    result = get_article(db, 99999)
    assert result is None


# ---------------------------------------------------------------------------
# get_articles
# ---------------------------------------------------------------------------


def test_get_articles_empty_db(db):
    """get_articles on empty DB returns empty list and total=0."""
    articles, total = get_articles(db)
    assert articles == []
    assert total == 0


def test_get_articles_returns_all(db, sample_create_data):
    """get_articles returns all created articles."""
    create_article(db, sample_create_data)
    create_article(db, sample_create_data)
    create_article(db, sample_create_data)
    articles, total = get_articles(db)
    assert total == 3
    assert len(articles) == 3


def test_get_articles_pagination_skip(db, sample_create_data):
    """get_articles with skip=2 skips first two articles."""
    for _ in range(4):
        create_article(db, sample_create_data)
    articles, total = get_articles(db, skip=2, limit=10)
    assert total == 4
    assert len(articles) == 2


def test_get_articles_pagination_limit(db, sample_create_data):
    """get_articles with limit=2 returns only 2 articles."""
    for _ in range(5):
        create_article(db, sample_create_data)
    articles, total = get_articles(db, skip=0, limit=2)
    assert total == 5
    assert len(articles) == 2


def test_get_articles_skip_beyond_total(db, sample_create_data):
    """get_articles with skip >= total returns empty list."""
    create_article(db, sample_create_data)
    articles, total = get_articles(db, skip=100, limit=10)
    assert total == 1
    assert articles == []


def test_get_articles_ordered_by_id(db):
    """get_articles returns articles ordered by ID ascending."""
    titles = ["Charlie", "Alpha", "Beta"]
    for title in titles:
        data = ArticleCreate(title=title, body="body", author="auth")
        create_article(db, data)
    articles, _ = get_articles(db)
    ids = [a.id for a in articles]
    assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# update_article
# ---------------------------------------------------------------------------


def test_update_article_title(db, sample_create_data):
    """update_article changes the title."""
    article = create_article(db, sample_create_data)
    update_data = ArticleUpdate(title="New Title")
    updated = update_article(db, article.id, update_data)
    assert updated is not None
    assert updated.title == "New Title"
    assert updated.body == sample_create_data.body


def test_update_article_status(db, sample_create_data):
    """update_article changes the status."""
    article = create_article(db, sample_create_data)
    update_data = ArticleUpdate(status=ArticleStatus.published)
    updated = update_article(db, article.id, update_data)
    assert updated.status == ArticleStatus.published


def test_update_article_multiple_fields(db, sample_create_data):
    """update_article can update multiple fields at once."""
    article = create_article(db, sample_create_data)
    update_data = ArticleUpdate(
        title="New Title", body="New body", author="New Author"
    )
    updated = update_article(db, article.id, update_data)
    assert updated.title == "New Title"
    assert updated.body == "New body"
    assert updated.author == "New Author"


def test_update_article_no_fields_leaves_unchanged(db, sample_create_data):
    """update_article with no fields set leaves article unchanged."""
    article = create_article(db, sample_create_data)
    original_title = article.title
    update_data = ArticleUpdate()
    updated = update_article(db, article.id, update_data)
    assert updated.title == original_title


def test_update_article_nonexistent_returns_none(db):
    """update_article on a non-existent ID returns None."""
    update_data = ArticleUpdate(title="Ghost")
    result = update_article(db, 99999, update_data)
    assert result is None


# ---------------------------------------------------------------------------
# delete_article
# ---------------------------------------------------------------------------


def test_delete_article_returns_true(db, sample_create_data):
    """delete_article returns True when article is found and deleted."""
    article = create_article(db, sample_create_data)
    result = delete_article(db, article.id)
    assert result is True


def test_delete_article_removes_from_db(db, sample_create_data):
    """After deletion, get_article returns None."""
    article = create_article(db, sample_create_data)
    delete_article(db, article.id)
    assert get_article(db, article.id) is None


def test_delete_article_nonexistent_returns_false(db):
    """delete_article returns False for a non-existent ID."""
    result = delete_article(db, 99999)
    assert result is False


def test_delete_article_only_deletes_target(db, sample_create_data):
    """Deleting one article does not affect others."""
    a1 = create_article(db, sample_create_data)
    a2 = create_article(db, sample_create_data)
    delete_article(db, a1.id)
    assert get_article(db, a2.id) is not None
    _, total = get_articles(db)
    assert total == 1
