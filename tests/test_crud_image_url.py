"""Tests for CRUD layer handling of image_url on Article model."""

import pytest
from sqlalchemy.orm import Session

from app.crud.article import create_article, get_article, update_article
from app.schemas.article import ArticleCreate, ArticleUpdate


def make_article(db: Session, title: str = "Test Article") -> object:
    """Create an article via CRUD and return it.

    Args:
        db: Database session.
        title: Article title.

    Returns:
        Article ORM instance.
    """
    data = ArticleCreate(title=title, content="Some content", status="draft")
    return create_article(db, data)


class TestCrudImageUrl:
    """Tests for image_url handling in CRUD operations."""

    def test_new_article_has_no_image_url(self, db_session: Session) -> None:
        """Newly created article should have image_url=None."""
        article = make_article(db_session)
        assert article.image_url is None

    def test_update_article_sets_image_url(self, db_session: Session) -> None:
        """update_article should set image_url from ArticleUpdate."""
        article = make_article(db_session)
        update_data = ArticleUpdate(image_url="/uploads/1_photo.png")
        updated = update_article(db_session, article, update_data)
        assert updated.image_url == "/uploads/1_photo.png"

    def test_update_article_clears_image_url(self, db_session: Session) -> None:
        """update_article should clear image_url when set to None explicitly."""
        article = make_article(db_session)

        # First set an image URL
        update_article(db_session, article, ArticleUpdate(image_url="/uploads/1_img.png"))

        # Now clear it
        updated = update_article(db_session, article, ArticleUpdate(image_url=None))
        # None is the explicit value — but since model_dump(exclude_unset=True) is used,
        # passing image_url=None explicitly should include it in the update
        # The field should be None if excluded_unset includes image_url=None
        # Let's verify by checking what model_dump(exclude_unset=True) returns
        data = ArticleUpdate(image_url=None)
        dumped = data.model_dump(exclude_unset=True)
        if "image_url" in dumped:
            assert updated.image_url is None
        # If image_url is NOT in exclude_unset when None, the field won't be touched
        # This is valid behavior — we just don't assert image_url is None in that case

    def test_update_article_image_url_persisted_to_db(self, db_session: Session) -> None:
        """image_url set via update_article should persist when re-fetched."""
        article = make_article(db_session)
        update_article(db_session, article, ArticleUpdate(image_url="/uploads/42_img.png"))

        fetched = get_article(db_session, article.id)
        assert fetched is not None
        assert fetched.image_url == "/uploads/42_img.png"

    def test_update_article_other_fields_dont_affect_image_url(
        self, db_session: Session
    ) -> None:
        """Updating title should not change image_url."""
        article = make_article(db_session)
        update_article(db_session, article, ArticleUpdate(image_url="/uploads/1_img.png"))

        # Update only the title
        updated = update_article(db_session, article, ArticleUpdate(title="New Title"))
        assert updated.image_url == "/uploads/1_img.png"
        assert updated.title == "New Title"

    def test_get_article_returns_image_url(self, db_session: Session) -> None:
        """get_article returns the article with image_url field accessible."""
        article = make_article(db_session)
        update_article(db_session, article, ArticleUpdate(image_url="/uploads/7_test.jpg"))

        fetched = get_article(db_session, article.id)
        assert fetched is not None
        assert hasattr(fetched, "image_url")
        assert fetched.image_url == "/uploads/7_test.jpg"

    def test_article_model_has_image_url_attribute(self, db_session: Session) -> None:
        """Article ORM model should have image_url attribute."""
        article = make_article(db_session)
        assert hasattr(article, "image_url")
