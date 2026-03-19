"""Database engine, session factory, and base model configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def get_db():
    """Yield a database session and ensure it is closed after use.

    Yields:
        Session: A SQLAlchemy database session.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all database tables defined in the ORM models.

    Uses the metadata from Base to create all tables that do not yet exist.
    """
    Base.metadata.create_all(bind=engine)
