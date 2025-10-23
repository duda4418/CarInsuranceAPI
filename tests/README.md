# Testing Guide

This folder contains test suites for the Car Insurance API.

## Structure
```
tests/
  conftest.py        # Shared fixtures (FastAPI app + DB session overrides)
  api/               # HTTP API endpoint tests
  services/          # Business/service layer tests
  utils/             # Factories & helpers for test data
```

## Quick Start
Install test dependencies (PowerShell):
```powershell
pip install pytest pytest-cov httpx faker
```
Run tests with coverage:
```powershell
pytest --cov=. --cov-report=term-missing
```

## Concepts
- Arrange: set up data / state
- Act: call function or endpoint
- Assert: verify result (status code, JSON, database changes)

## Fixtures
`conftest.py` defines:
- `client`: FastAPI TestClient using in-memory SQLite.
- `db_session`: Direct SQLAlchemy session if you need to manipulate models.

## Factories
`tests/utils/factories.py` has small helpers to create cars, policies, claims without verbose setup.

## Adding Tests
Create a file `tests/api/test_<resource>_api.py` or `tests/services/test_<service>.py`.
Use existing examples as templates.

## Async Tests
If you introduce async service functions, install `pytest-asyncio` and mark tests:
```python
import pytest

@pytest.mark.asyncio
async def test_something_async():
    ...
```

## Coverage Target
Aim for ≥80%. Use `--cov` output to identify untested lines and add focused tests.

## Next Ideas
- Add history endpoint tests when implemented.
- Expand policy validation (e.g. start < end date logic).
- Use Faker for more randomized inputs once basics are stable.
