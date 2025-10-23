"""Claim service: creation and update logic."""
from sqlalchemy.orm import Session
from db.models import Claim, Car
from services.exceptions import NotFoundError, ValidationError
from api.schemas import ClaimCreate


def create_claim(db: Session, car_id: int, data: ClaimCreate) -> Claim:
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise NotFoundError("Car", car_id)

    if not data.description or not data.description.strip():
        raise ValidationError("Description must not be empty")

    if data.amount is None or data.amount <= 0:
        raise ValidationError("Amount must be greater than 0")

    claim = Claim(
        car_id=car_id,
        claim_date=data.claim_date,
        description=data.description,
        amount=data.amount
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)

    return claim


def update_claim(db: Session, claim: Claim, data: ClaimCreate) -> Claim:
    if not data.description or not data.description.strip():
        raise ValidationError("Description must not be empty")

    if data.amount is None or data.amount <= 0:
        raise ValidationError("Amount must be greater than 0")

    if data.car_id != claim.car_id:
        car = db.query(Car).filter(Car.id == data.car_id).first()
        if not car:
            raise NotFoundError("Car", data.car_id)
        claim.car_id = data.car_id
    claim.claim_date = data.claim_date
    claim.description = data.description
    claim.amount = data.amount
    db.commit()
    db.refresh(claim)

    return claim


def get_claim_by_id(db: Session, claim_id: int) -> Claim | None:
    return db.query(Claim).filter(Claim.id == claim_id).first()
