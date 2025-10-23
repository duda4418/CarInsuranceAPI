"""Simple factory helpers for creating model instances in tests.
Avoids using heavy external libs until needed.
"""
from datetime import date
from sqlalchemy.orm import Session
from db.models import Car, InsurancePolicy, Claim, Owner


_car_counter = 0
_owner_counter = 0

def create_owner(db: Session, name: str | None = None, email: str | None = None) -> Owner:
    global _owner_counter
    _owner_counter += 1
    name = name or f"Owner{_owner_counter}"
    email = email or f"owner{_owner_counter}@example.com"
    owner = Owner(name=name, email=email)
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner


def create_car(
    db: Session,
    make: str = "Toyota",
    model: str = "Corolla",
    vin: str | None = None,
    owner: Owner | None = None,
    year: int | None = 2025,
) -> Car:
    global _car_counter
    _car_counter += 1
    if owner is None:
        owner = create_owner(db)
    vin = vin or f"VIN{_car_counter:05d}"
    car = Car(vin=vin, make=make, model=model, owner_id=owner.id, year_of_manufacture=year)
    db.add(car)
    db.commit()
    db.refresh(car)
    return car


def create_policy(
    db: Session,
    car: Car | None = None,
    provider: str = "Acme Insurance",
    start: date | None = None,
    end: date | None = None,
    logged_expiry_at=None,
) -> InsurancePolicy:
    if car is None:
        car = create_car(db)
    start = start or date(2025, 1, 1)
    end = end or date(2025, 12, 31)
    policy = InsurancePolicy(
        car_id=car.id,
        provider=provider,
        start_date=start,
        end_date=end,
        logged_expiry_at=logged_expiry_at,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def create_claim(
    db: Session,
    car: Car | None = None,
    description: str = "Broken mirror",
    amount: float = 120.50,
    claim_date: date | None = None,
) -> Claim:
    if car is None:
        car = create_car(db)
    claim_date = claim_date or date(2025, 2, 15)
    claim = Claim(
        car_id=car.id,
        description=description,
        amount=amount,
        claim_date=claim_date,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim

__all__ = [
    "create_owner",
    "create_car",
    "create_policy",
    "create_claim",
]
