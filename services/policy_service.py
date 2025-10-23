"""Policy service: creation, update, active policy queries."""
from datetime import date
from sqlalchemy.orm import Session
from db.models import InsurancePolicy, Car
from services.exceptions import NotFoundError, ValidationError
from api.schemas import InsurancePolicyCreate


def create_policy(db: Session, car_id: int, data: InsurancePolicyCreate) -> InsurancePolicy:
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise NotFoundError("Car", car_id)

    if data.end_date is None or data.end_date < data.start_date:
        raise ValidationError("end_date must be present and >= start_date")

    policy = InsurancePolicy(
        car_id=car_id,
        provider=data.provider,
        start_date=data.start_date,
        end_date=data.end_date,
        logged_expiry_at=data.logged_expiry_at,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)

    return policy


def update_policy(db: Session, policy: InsurancePolicy, data: InsurancePolicyCreate) -> InsurancePolicy:
    if data.end_date is None or data.end_date < data.start_date:
        raise ValidationError("end_date must be present and >= start_date")

    # Car reassignment
    if data.car_id != policy.car_id:
        car = db.query(Car).filter(Car.id == data.car_id).first()
        if not car:
            raise NotFoundError("Car", data.car_id)
        policy.car_id = data.car_id
    policy.provider = data.provider
    policy.start_date = data.start_date
    policy.end_date = data.end_date
    policy.logged_expiry_at = data.logged_expiry_at
    db.commit()
    db.refresh(policy)

    return policy


def get_policy_by_id(db: Session, policy_id: int) -> InsurancePolicy | None:
    return db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()


def get_policies_for_car(db: Session, car_id: int) -> list[InsurancePolicy]:
    return db.query(InsurancePolicy).filter(InsurancePolicy.car_id == car_id).all()


def get_active_policy(db: Session, car_id: int, on_date: date) -> InsurancePolicy | None:
    return db.query(InsurancePolicy).filter(
        InsurancePolicy.car_id == car_id,
        InsurancePolicy.start_date <= on_date,
        InsurancePolicy.end_date >= on_date
    ).first()
