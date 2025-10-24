"""Pytest fixtures shared across test suites."""

import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.base import Base
from db.session import get_db
from main import create_app

# In-memory SQLite for fast tests
# StaticPool keeps the same connection for the lifespan of tests so data persists across requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TESTING_SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create schema once
Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator:
    """Yield a database session for dependency override in tests."""
    db = TESTING_SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()


# FastAPI dependency override applied in fixture
app = create_app(enable_scheduler=False, configure_logs=False)
app.dependency_overrides[get_db] = override_get_db


def get_test_client() -> TestClient:
    """Return a TestClient instance for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Session-scoped fixture for FastAPI test client."""
    yield get_test_client()


@pytest.fixture()
def db_session_fixture() -> Generator:
    """Fixture for providing a database session to tests."""
    yield from override_get_db()


@pytest.fixture(autouse=True)
def clean_database(db_session_fixture):
    """Clear all tables before each test to ensure isolation.

    This prevents earlier tests (that insert rows) from affecting tests that
    expect an empty list (like list endpoints). Using reversed sorted_tables to
    respect FK constraints.
    """
    for table in reversed(Base.metadata.sorted_tables):
        db_session_fixture.execute(table.delete())
    db_session_fixture.commit()
