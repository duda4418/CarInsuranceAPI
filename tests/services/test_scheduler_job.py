from datetime import datetime
from unittest.mock import patch

from db.models import InsurancePolicy
from services.scheduler import _run_policy_expiry_job
from tests.utils.factories import create_car


def test_policy_expiry_job_marks_unlogged(db_session_fixture):
    # Arrange: create a policy expiring today with no logged_expiry_at
    car = create_car(db_session_fixture, make="Test", model="Car")

    today = datetime.now().date()
    policy = InsurancePolicy(
        car_id=car.id,
        provider="Provider",
        start_date=today,
        end_date=today,
    )
    db_session_fixture.add(policy)
    db_session_fixture.commit()
    db_session_fixture.refresh(policy)

    def fake_get_db():
        # Create an independent session sharing the same engine (StaticPool ensures same memory DB)
        from sqlalchemy.orm import sessionmaker

        SessionLocalTest = sessionmaker(
            bind=db_session_fixture.bind, autoflush=False, autocommit=False, future=True
        )
        test_db = SessionLocalTest()
        try:
            yield test_db
        finally:
            test_db.close()

    with patch("services.scheduler.acquire_lock", return_value=True), patch(
        "services.scheduler.release_lock", return_value=None
    ), patch("services.scheduler.get_db", fake_get_db):
        # Act
        _run_policy_expiry_job()

    # Assert
    # Use a fresh session to avoid stale identity map
    from sqlalchemy.orm import sessionmaker

    SessionLocalTest = sessionmaker(
    bind=db_session_fixture.bind, autoflush=False, autocommit=False, future=True
    )
    fresh = SessionLocalTest()
    try:
        updated = fresh.get(InsurancePolicy, policy.id)
    finally:
        fresh.close()
    assert updated.logged_expiry_at is not None
