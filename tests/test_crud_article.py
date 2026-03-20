"""Unit tests for CRUD operations in app/crud/article.py."""

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


@pytest.fixture()
def db():
    """Provide a fresh in-memory SQLite session for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def sample_article_data() -> dict:
    """Return a minimal valid article data dictionary."""
    return {
        "title": "Sample Title",
        "body": "Sample body text",
        "status": ArticleStatus.draft,
        "author": "Test Author",
        "category_ids": [],
    }


# ---------------------------------------------------------------------------
# create_article
# ---------------------------------------------------------------------------


def test_create_article_happy_path(db, sample_article_data) -> None:
    """Creating an article returns an Article with correct fields."""
    article = create_article(db, sample_article_data.copy())

    assert article.id is not None
    assert article.title == "Sample Title"
    assert article.body == "Sample body text"
    assert article.status == ArticleStatus.draft
    assert article.author == "Test Author"
    assert article.categories == []


def test_create_article_with_categories(db) -> None:
    """Creating an article with category_ids should link the categories."""
    from app.models.category import Category

    cat = Category(name="Tech")
    db.add(cat)
    db.commit()
    db.refresh(cat)

    data = {
        "title": "Tech Article",
        "body": "Body text",
        "status": ArticleStatus.published,
        "author": "Author",
        "category_ids": [cat.id],
    }
    article = create_article(db, data)

    assert len(article.categories) == 1
    assert article.categories[0].name == "Tech"


# ---------------------------------------------------------------------------
# get_article
# ---------------------------------------------------------------------------


def test_get_article_existing(db, sample_article_data) -> None:
    """get_article returns the article when it exists."""
    created = create_article(db, sample_article_data.copy())
    fetched = get_article(db, created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Sample Title"


def test_get_article_nonexistent(db) -> None:
    """get_article returns None for a non-existent ID."""
    result = get_article(db, 9999)
    assert result is None


# ---------------------------------------------------------------------------
# get_articles — search
# ---------------------------------------------------------------------------


def test_get_articles_search_by_title(db) -> None:
    """Search by title substring returns matching articles."""
    create_article(db, {"title": "Python Basics", "body": "intro", "status": ArticleStatus.draft, "author": "A", "category_ids": []})
    create_article(db, {"title": "Java Basics", "body": "intro", "status": ArticleStatus.draft, "author": "A", "category_ids": []})

    articles, total = get_articles(db, search="Python")
    assert total == 1
    assert articles[0].title == "Python Basics"


def test_get_articles_search_by_body(db) -> None:
    """Search by body substring returns matching articles."""
    create_article(db, {"title": "Article 1", "body": "unique_search_xyz content", "status": ArticleStatus.draft, "author": "A", "category_ids": []})
    create_article(db, {"title": "Article 2", "body": "other content", "status": ArticleStatus.draft, "author": "A", "category_ids": []})

    articles, total = get_articles(db, search="unique_search_xyz")
    assert total == 1
    assert articles[0].title == "Article 1"


def test_get_articles_search_case_insensitive(db) -> None:
    """ilike search should be case-insensitive."""
    create_article(db, {"title": "CamelCase Match", "body": "body", "status": ArticleStatus.draft, "author": "A", "category_ids": []})

    articles, total = get_articles(db, search="camelcase match")
    assert total == 1


def test_get_articles_search_no_match(db) -> None:
    """Search with no match returns empty list and total=0."""
    create_article(db, {"title": "Some Article", "body": "body", "status": ArticleStatus.draft, "author": "A", "category_ids": []})

    articles, total = get_articles(db, search="zzznomatch999")
    assert total == 0
    assert articles == []


# ---------------------------------------------------------------------------
# get_articles — filters
# ---------------------------------------------------------------------------


def test_get_articles_filter_by_status(db) -> None:
    """Filter by status returns only articles with matching status."""
    create_article(db, {"title": "Draft A", "body": "b", "status": ArticleStatus.draft, "author": "A", "category_ids": []})
    create_article(db, {"title": "Published A", "body": "b", "status": ArticleStatus.published, "author": "A", "category_ids": []})

    articles, total = get_articles(db, status=ArticleStatus.published)
    assert total == 1
    assert articles[0].status == ArticleStatus.published


def test_get_articles_filter_by_author(db) -> None:
    """Filter by author returns only that author's articles."""
    create_article(db, {"title": "By Alice", "body": "b", "status": ArticleStatus.draft, "author": "Alice", "category_ids": []})
    create_article(db, {"title": "By Bob", "body": "b", "status": ArticleStatus.draft, "author": "Bob", "category_ids": []})

    articles, total = get_articles(db, author="Alice")
    assert total == 1
    assert articles[0].author == "Alice"


def test_get_articles_filter_by_category(db) -> None:
    """Filter by category_id returns only articles in that category."""
    from app.models.category import Category

    cat = Category(name="Sports")
    db.add(cat)
    db.commit()
    db.refresh(cat)

    create_article(db, {"title": "Sports Article", "body": "b", "status": ArticleStatus.draft, "author": "A", "category_ids": [cat.id]})
    create_article(db, {"title": "Other Article", "body": "b", "status": ArticleStatus.draft, "author": "A", "category_ids": []})

    articles, total = get_articles(db, category_id=cat.id)
    assert total == 1
    assert articles[0].title == "Sports Article"


# ---------------------------------------------------------------------------
# get_articles — pagination
# ---------------------------------------------------------------------------


def test_get_articles_pagination(db) -> None:
    """Pagination returns correct subset and total count."""
    for i in range(5):
        create_article(db, {"title": f"Article {i}", "body": "b", "status": ArticleStatus.draft, "author": "A", "category_ids": []})

    articles_p1, total = get_articles(db, page=1, per_page=2)
    assert total == 5
    assert len(articles_p1) == 2

    articles_p3, total2 = get_articles(db, page=3, per_page=2)
    assert total2 == 5
    assert len(articles_p3) == 1


def test_get_articles_returns_all_when_no_filters(db) -> None:
    """get_articles with no filters returns all articles."""
    for i in range(3):
        create_article(db, {"title": f"T{i}", "body": "b", "status": ArticleStatus.draft, "author": "A", "category_ids": []})

    articles, total = get_articles(db)
    assert total == 3
    assert len(articles) == 3


# ---------------------------------------------------------------------------
# update_article
# ---------------------------------------------------------------------------


def test_update_article_happy_path(db, sample_article_data) -> None:
    """Updating existing fields returns updated article."""
    article = create_article(db, sample_article_data.copy())
    updated = update_article(db, article.id, {"title": "New Title"})

    assert updated is not None
    assert updated.title == "New Title"
    assert updated.body == "Sample body text"


def test_update_article_nonexistent(db) -> None:
    """Updating a non-existent article returns None."""
    result = update_article(db, 9999, {"title": "X"})
    assert result is None


# ---------------------------------------------------------------------------
# delete_article
# ---------------------------------------------------------------------------


def test_delete_article_happy_path(db, sample_article_data) -> None:
    """Deleting an existing article returns True."""
    article = create_article(db, sample_article_data.copy())
    result = delete_article(db, article.id)

    assert result is True
    assert get_article(db, article.id) is None


def test_delete_article_nonexistent(db) -> None:
    """Deleting a non-existent article returns False."""
    result = delete_article(db, 9999)
    assert result is False
