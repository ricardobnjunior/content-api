"""Database engine, session factory, base model, and dependency utilities."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


def get_db():
    """Yield a database session and ensure it is closed after use.

    Yields:
        Session: SQLAlchemy synchronous database session.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables defined by ORM models in the database.

    This function is safe to call multiple times; existing tables are not
    dropped or modified.
    """
    Base.metadata.create_all(bind=engine)
