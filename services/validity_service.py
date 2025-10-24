"""Insurance validity orchestration service."""
from datetime import date
from sqlalchemy.orm import Session
from db.models import Car
from services.policy_service import get_active_policy
from services.exceptions import NotFoundError, ValidationError


def is_insurance_valid(db: Session, car_id: int, on_date_str: str) -> bool:
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise NotFoundError("Car", car_id)

    try:
        year, month, day = map(int, on_date_str.split('-'))
        on_date = date(year, month, day)
    except Exception:
        raise ValidationError("Invalid date format; expected YYYY-MM-DD")

    if on_date.year < 1900 or on_date.year > 2100:
        raise ValidationError("Date out of range")

    return get_active_policy(db, car_id, on_date) is not None
