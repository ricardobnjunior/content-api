"""Tests for article CRUD operations including image_url handling."""

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
from app.schemas.article import ArticleCreate, ArticleUpdate

TEST_DB_URL = "sqlite:///:memory:"

_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture(scope="module", autouse=True)
def create_tables():
    """Create all ORM tables for the test module."""
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture
def db():
    """Provide a clean database session per test with rollback."""
    connection = _engine.connect()
    transaction = connection.begin()
    session = _SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def test_update_article_sets_image_url(db) -> None:
    """Test that update_article sets image_url when provided."""
    article = create_article(db, ArticleCreate(title="My Article", status="draft"))
    assert article.image_url is None

    updated = update_article(
        db,
        article,
        ArticleUpdate(),
        image_url="/uploads/1_photo.jpg",
    )
    assert updated.image_url == "/uploads/1_photo.jpg"


def test_update_article_image_url_none_does_not_clear(db) -> None:
    """Test that passing image_url=None to update_article does not overwrite existing URL."""
    article = create_article(db, ArticleCreate(title="Article With Image", status="draft"))
    article.image_url = "/uploads/existing.jpg"
    db.commit()
    db.refresh(article)

    updated = update_article(
        db,
        article,
        ArticleUpdate(title="Updated Title"),
        image_url=None,
    )
    # image_url=None means "not provided" — existing value should be preserved
    assert updated.image_url == "/uploads/existing.jpg"


def test_update_article_title_and_image_url(db) -> None:
    """Test updating both title and image_url in a single call."""
    article = create_article(db, ArticleCreate(title="Original", status="draft"))

    updated = update_article(
        db,
        article,
        ArticleUpdate(title="New Title"),
        image_url="/uploads/5_new.png",
    )
    assert updated.title == "New Title"
    assert updated.image_url == "/uploads/5_new.png"


def test_create_article_image_url_is_none(db) -> None:
    """Test that a newly created article has image_url as None by default."""
    article = create_article(db, ArticleCreate(title="No Image", status="published"))
    assert article.image_url is None


def test_get_article_returns_image_url(db) -> None:
    """Test that get_article returns the correct image_url field."""
    article = create_article(db, ArticleCreate(title="With Image", status="draft"))
    article.image_url = "/uploads/7_img.jpg"
    db.commit()
    db.refresh(article)

    fetched = get_article(db, article.id)
    assert fetched is not None
    assert fetched.image_url == "/uploads/7_img.jpg"


def test_get_article_not_found_returns_none(db) -> None:
    """Test that get_article returns None for a non-existent ID."""
    result = get_article(db, 999999)
    assert result is None


def test_delete_article(db) -> None:
    """Test that delete_article removes the article from the database."""
    article = create_article(db, ArticleCreate(title="To Delete", status="draft"))
    article_id = article.id

    delete_article(db, article)

    fetched = get_article(db, article_id)
    assert fetched is None


def test_get_articles_pagination(db) -> None:
    """Test get_articles returns correct pagination metadata."""
    for i in range(5):
        create_article(db, ArticleCreate(title=f"Article {i}", status="draft"))

    result = get_articles(db, page=1, per_page=3)
    assert "items" in result
    assert "meta" in result
    assert result["meta"]["per_page"] == 3
    assert len(result["items"]) <= 3
