"""SQLAlchemy session and engine setup."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.settings import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

# Session factory for ORM sessions
SESSION_LOCAL = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)


def get_db():
    """Yield a database session for dependency injection."""
    db = SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()
