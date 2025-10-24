import pytest

from services.validity_service import is_insurance_valid
from tests.utils.factories import create_car, create_policy


def test_valid_true(db_session_fixture):
    car = create_car(db_session_fixture)
    create_policy(db_session_fixture, car, start=None, end=None)  # defaults 2025 full year
    assert is_insurance_valid(db_session_fixture, car.id, "2025-06-01") is True


def test_valid_false(db_session_fixture):
    car = create_car(db_session_fixture)
    # Policy for January only
    create_policy(db_session_fixture, car, start=None, end=None)  # default full year
    # Make it not cover June by overwriting end_date
    for p in car.policies:
        p.end_date = p.start_date.replace(month=1, day=31)
    db_session_fixture.commit()
    assert is_insurance_valid(db_session_fixture, car.id, "2025-06-01") is False


def test_car_not_found(db_session_fixture):
    with pytest.raises(Exception) as exc:
        is_insurance_valid(db_session_fixture, 9999, "2025-01-01")
    assert "Car" in str(exc.value)


def test_invalid_date_format(db_session_fixture):
    car = create_car(db_session_fixture)
    with pytest.raises(Exception) as exc:
        is_insurance_valid(db_session_fixture, car.id, "2025/01/01")
    assert "Invalid date format" in str(exc.value)


def test_date_out_of_range(db_session_fixture):
    car = create_car(db_session_fixture)
    with pytest.raises(Exception) as exc:
        is_insurance_valid(db_session_fixture, car.id, "1800-01-01")
    assert "Date out of range" in str(exc.value)


def test_date_out_of_range_high_year(db_session_fixture):
    car = create_car(db_session_fixture)
    with pytest.raises(Exception) as exc:
        is_insurance_valid(db_session_fixture, car.id, "2201-07-01")
    assert "Date out of range" in str(exc.value)
