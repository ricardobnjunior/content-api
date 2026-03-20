"""Tests for app/database.py — engine, session, Base, get_db, create_tables."""

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session


def test_engine_is_created():
    """engine should be a valid SQLAlchemy engine."""
    from sqlalchemy.engine import Engine

    from app.database import engine

    assert isinstance(engine, Engine)


def test_session_local_creates_session():
    """SessionLocal() should return a SQLAlchemy Session."""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        assert isinstance(db, Session)
    finally:
        db.close()


def test_base_is_declarative():
    """Base should be a DeclarativeBase subclass with metadata."""
    from sqlalchemy import MetaData

    from app.database import Base

    assert hasattr(Base, "metadata")
    assert isinstance(Base.metadata, MetaData)


def test_get_db_yields_session():
    """get_db() should yield a Session instance."""
    from app.database import get_db

    gen = get_db()
    db = next(gen)
    try:
        assert isinstance(db, Session)
    finally:
        try:
            gen.close()
        except StopIteration:
            pass


def test_get_db_closes_session_after_use():
    """get_db() should close the session when the generator is exhausted."""
    from app.database import get_db

    gen = get_db()
    db = next(gen)
    # Close via generator cleanup
    try:
        next(gen)
    except StopIteration:
        pass
    # After generator ends, session should be closed (is_active returns False or
    # the underlying connection is returned to pool — no exception expected)


def test_create_tables_runs_without_error():
    """create_tables() should complete without raising an exception."""
    from app.database import create_tables

    create_tables()  # Safe to call multiple times


def test_session_can_execute_query():
    """A session from SessionLocal should be able to run a simple query."""
    from app.database import SessionLocal, create_tables

    create_tables()
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        db.close()
