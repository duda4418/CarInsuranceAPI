"""Claim service: creation and update logic."""

from sqlalchemy.orm import Session

from api.schemas import ClaimCreate, ClaimCreateNested
from core.logging import get_logger
from db.models import Car, Claim
from services.exceptions import NotFoundError

log = get_logger()


def create_claim(
    db: Session, car_id: int, data: ClaimCreate | ClaimCreateNested
) -> Claim:
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise NotFoundError("Car", car_id)

    claim = Claim(
        car_id=car_id,
        claim_date=data.claim_date,
        description=data.description,
        amount=data.amount,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)

    log.info(
        "claim_created",
        claimId=claim.id,
        carId=claim.car_id,
        amount=float(claim.amount),
    )
    return claim


def update_claim(db: Session, claim: Claim, data: ClaimCreate) -> Claim:
    claim.claim_date = data.claim_date
    claim.description = data.description
    claim.amount = data.amount
    db.commit()
    db.refresh(claim)
    log.info(
        "claim_updated",
        claimId=claim.id,
        carId=claim.car_id,
        amount=float(claim.amount),
    )
    return claim


def get_claim_by_id(db: Session, claim_id: int) -> Claim | None:
    return db.query(Claim).filter(Claim.id == claim_id).first()


def list_claims(db: Session) -> list[Claim]:
    return db.query(Claim).all()


def delete_claim(db: Session, claim: Claim) -> None:
    claim_id = claim.id
    car_id = claim.car_id
    db.delete(claim)
    db.commit()
    log.info("claim_deleted", claimId=claim_id, carId=car_id)
