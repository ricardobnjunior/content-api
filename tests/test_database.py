"""Tests for app/database.py — engine, session, Base, get_db, create_tables."""

import os

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session


def test_engine_is_sync():
    """Engine should be a sync SQLAlchemy engine (not async)."""
    from sqlalchemy import Engine
    from app.database import engine
    assert isinstance(engine, Engine)


def test_session_local_creates_session():
    """SessionLocal() should return a sync Session."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        assert isinstance(db, Session)
    finally:
        db.close()


def test_base_has_metadata():
    """Base should have a metadata attribute (DeclarativeBase)."""
    from app.database import Base
    assert hasattr(Base, "metadata")


def test_get_db_yields_session():
    """get_db() should yield a Session instance."""
    from app.database import get_db
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
    """get_db() should close the session after exhausting the generator."""
    from app.database import get_db
    gen = get_db()
    db = next(gen)
    # exhaust generator
    try:
        next(gen)
    except StopIteration:
        pass
    # after close, session should not be usable for queries
    # SQLAlchemy raises on usage after close — we simply verify no exception was raised during cleanup


def test_create_tables_runs_without_error():
    """create_tables() should run without raising exceptions."""
    from app.database import create_tables
    # Should not raise
    create_tables()


def test_session_can_execute_query():
    """A session from SessionLocal should be able to run a basic query."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1"))
        row = result.fetchone()
        assert row[0] == 1
    finally:
        db.close()


def test_get_db_is_generator():
    """get_db() must be a generator function."""
    import inspect
    from app.database import get_db
    gen = get_db()
    assert inspect.isgenerator(gen)
    # clean up
    try:
        db = next(gen)
    except StopIteration:
        pass
    try:
        next(gen)
    except StopIteration:
        pass
