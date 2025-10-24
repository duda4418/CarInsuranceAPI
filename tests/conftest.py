"""Pytest fixtures shared across test suites."""
from typing import Generator
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import create_app  # noqa: E402
from db.base import Base  # noqa: E402
from db.session import get_db  # noqa: E402

# In-memory SQLite for fast tests
# StaticPool keeps the same connection for the lifespan of tests so data persists across requests
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create schema once
Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI dependency override applied in fixture
app = create_app(enable_scheduler=False, configure_logs=False)
app.dependency_overrides[get_db] = override_get_db


def get_test_client() -> TestClient:
    return TestClient(app)


# Pytest fixture for client
import pytest

@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    yield get_test_client()

@pytest.fixture()
def db_session() -> Generator:
    yield from override_get_db()


@pytest.fixture(autouse=True)
def clean_database(db_session):
    """Clear all tables before each test to ensure isolation.

    This prevents earlier tests (that insert rows) from affecting tests that
    expect an empty list (like list endpoints). Using reversed sorted_tables to
    respect FK constraints.
    """
    from db.base import Base  # local import to avoid circular early loads
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
