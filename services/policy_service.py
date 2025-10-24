"""Policy service: creation, update, active policy queries."""

from datetime import date, datetime

from sqlalchemy.orm import Session

from api.schemas import InsurancePolicyCreate, InsurancePolicyCreateNested
from core.logging import get_logger
from db.models import Car, InsurancePolicy
from services.exceptions import NotFoundError, ValidationError

log = get_logger()


def create_policy(
    db: Session, car_id: int, data: InsurancePolicyCreate | InsurancePolicyCreateNested
) -> InsurancePolicy:
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise NotFoundError("Car", car_id)

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

    log.info(
        "policy_created",
        policyId=policy.id,
        carId=policy.car_id,
        provider=policy.provider,
    )
    return policy


def update_policy(
    db: Session, policy: InsurancePolicy, data: InsurancePolicyCreate
) -> InsurancePolicy:
    policy.provider = data.provider
    policy.start_date = data.start_date
    policy.end_date = data.end_date
    policy.logged_expiry_at = data.logged_expiry_at
    db.commit()
    db.refresh(policy)
    log.info(
        "policy_updated",
        policyId=policy.id,
        carId=policy.car_id,
        provider=policy.provider,
    )
    return policy


def get_policy_by_id(db: Session, policy_id: int) -> InsurancePolicy | None:
    return db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()


def get_policies_for_car(db: Session, car_id: int) -> list[InsurancePolicy]:
    return db.query(InsurancePolicy).filter(InsurancePolicy.car_id == car_id).all()


def get_active_policy(
    db: Session, car_id: int, on_date: date
) -> InsurancePolicy | None:
    return (
        db.query(InsurancePolicy)
        .filter(
            InsurancePolicy.car_id == car_id,
            InsurancePolicy.start_date <= on_date,
            InsurancePolicy.end_date >= on_date,
        )
        .first()
    )


def get_unlogged_expiring_policies(
    db: Session, target_date: date
) -> list[InsurancePolicy]:
    """Return policies whose end_date equals target_date and logged_expiry_at is NULL."""
    return (
        db.query(InsurancePolicy)
        .filter(
            InsurancePolicy.end_date == target_date,
            InsurancePolicy.logged_expiry_at.is_(None),
        )
        .all()
    )


def mark_policy_logged(
    db: Session, policy: InsurancePolicy, logged_at: datetime
) -> None:
    policy.logged_expiry_at = logged_at
    db.add(policy)


def list_policies(db: Session) -> list[InsurancePolicy]:
    return db.query(InsurancePolicy).all()


def delete_policy(db: Session, policy: InsurancePolicy) -> None:
    policy_id = policy.id
    car_id = policy.car_id
    db.delete(policy)
    db.commit()
    log.info("policy_deleted", policyId=policy_id, carId=car_id)
