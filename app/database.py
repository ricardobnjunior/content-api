"""Database engine, session factory, and base model configuration."""

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
    """Base class for all SQLAlchemy ORM models."""


def get_db():
    """Yield a database session for use as a FastAPI dependency.

    Yields:
        Session: An active SQLAlchemy database session.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables defined in ORM models that have not yet been created."""
    Base.metadata.create_all(bind=engine)
