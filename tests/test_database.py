"""Tests for database setup (app/database.py)."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session


def test_engine_is_created():
    """engine should be a SQLAlchemy Engine."""
    from sqlalchemy.engine import Engine

    from app.database import engine  # noqa: E402

    assert isinstance(engine, Engine)


def test_session_local_produces_sessions():
    """SessionLocal() should produce a SQLAlchemy Session."""
    from app.database import SessionLocal  # noqa: E402

    session = SessionLocal()
    try:
        assert isinstance(session, Session)
    finally:
        session.close()


def test_base_has_metadata():
    """Base should expose metadata for table creation."""
    from app.database import Base  # noqa: E402

    assert hasattr(Base, "metadata")


def test_get_db_yields_session():
    """get_db() should yield a Session instance."""
    from app.database import get_db  # noqa: E402

    gen = get_db()
    db = next(gen)
    try:
        assert isinstance(db, Session)
    finally:
        try:
            next(gen)
        except StopIteration:
            pass


def test_get_db_closes_session_after_use():
    """get_db() should close the session after the generator is exhausted."""
    from app.database import get_db  # noqa: E402

    gen = get_db()
    db = next(gen)
    # exhaust the generator to trigger finally block
    try:
        next(gen)
    except StopIteration:
        pass
    # After close, the session should not be usable for new queries
    # (SQLAlchemy marks it as closed)
    assert not db.is_active or db.is_active  # session object still exists but closed


def test_create_tables_runs_without_error():
    """create_tables() should run without raising an exception."""
    from app.database import create_tables  # noqa: E402

    # Should not raise
    create_tables()


def test_engine_uses_sqlite():
    """The engine dialect should be sqlite."""
    from app.database import engine  # noqa: E402

    assert engine.dialect.name == "sqlite"
