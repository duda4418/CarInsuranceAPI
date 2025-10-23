from datetime import datetime
from unittest.mock import patch
from services.scheduler import _run_policy_expiry_job
from db.models import InsurancePolicy
from tests.utils.factories import create_car


def test_scheduler_lock_fail(db_session):
    # If lock acquisition fails, job returns early (no commit, no changes)
    with patch("services.scheduler.acquire_lock", return_value=False):
        _run_policy_expiry_job()  # Should do nothing
    # Nothing to assert besides no exception; optionally check no policies added


def test_scheduler_empty_expiring_list(db_session):
    # Lock succeeds but there are no policies expiring today -> early return
    with patch("services.scheduler.acquire_lock", return_value=True), \
        patch("services.scheduler.release_lock", return_value=None), \
        patch("services.scheduler.get_db", return_value=iter([db_session])):
        _run_policy_expiry_job()
    # No policies should be committed; nothing to assert except no errors


def test_scheduler_catchup_outside_window(db_session):
    # Create an expiring policy today
    car = create_car(db_session, vin="SCH1", make="M", model="X", year=2024)
    today = datetime(2025, 1, 1, 10, 30)  # Outside first hour
    policy = InsurancePolicy(car_id=car.id, provider="Prov", start_date=today.date(), end_date=today.date())
    db_session.add(policy); db_session.commit(); db_session.refresh(policy)

    class FakeDT(datetime):
        @classmethod
        def now(cls, tz=None):
            return today

    def fake_get_db():
        from sqlalchemy.orm import sessionmaker
        SessionLocalTest = sessionmaker(bind=db_session.bind, autoflush=False, autocommit=False, future=True)
        test_db = SessionLocalTest()
        try:
            yield test_db
        finally:
            test_db.close()

    with patch("services.scheduler.acquire_lock", return_value=True), \
         patch("services.scheduler.release_lock", return_value=None), \
         patch("services.scheduler.get_db", fake_get_db), \
         patch("services.scheduler.datetime", FakeDT):
        _run_policy_expiry_job()

    from sqlalchemy.orm import sessionmaker
    SessionLocalTest = sessionmaker(bind=db_session.bind, autoflush=False, autocommit=False, future=True)
    fresh = SessionLocalTest()
    try:
        updated = fresh.get(InsurancePolicy, policy.id)
    finally:
        fresh.close()
    assert updated.logged_expiry_at is not None
