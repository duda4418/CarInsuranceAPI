# db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings

# Create the SQLAlchemy engine using your DATABASE_URL from settings
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

# Session factory for ORM sessions
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# FastAPI dependency — yields a session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
