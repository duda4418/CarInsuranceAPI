"""Seed the PostgreSQL database with mock data.

Usage (from project root with venv active and docker db running):
    python scripts/seed.py --owners 10 --cars-per-owner 2 --policies-per-car 1 --claims-per-car 3 --purge

Flags:
    --owners              Number of owners to create
    --cars-per-owner      Number of cars per owner
    --policies-per-car    Number of insurance policies per car
    --claims-per-car      Number of claims per car
    --purge               If provided, existing data is deleted first (in FK-safe order)

The script is idempotent when --purge is used; otherwise it just appends.
"""

from __future__ import annotations

import argparse
import random
from datetime import date, timedelta
from decimal import Decimal

from faker import Faker
from sqlalchemy.orm import Session

from db import models
from db.session import SESSION_LOCAL

fake = Faker()

# -------------- Helpers --------------


def random_date_between(start: date, end: date) -> date:
    """Return a random date between start and end inclusive."""
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def create_owner(session: Session) -> models.Owner:
    owner = models.Owner(name=fake.name(), email=fake.unique.email())
    session.add(owner)
    return owner


def create_car(session: Session, owner: models.Owner) -> models.Car:
    vin = fake.unique.bothify(text="????????????????????????????????")[:32]
    car = models.Car(
        vin=vin,
        make=random.choice(["Ford", "Toyota", "BMW", "Audi", "Tesla", "VW", "Volvo"]),
        model=random.choice(
            ["S", "X", "CX-5", "Corolla", "Focus", "A4", "320", "Model 3"]
        ),
        year_of_manufacture=random.randint(2005, 2024),
        owner=owner,
    )
    session.add(car)
    return car


def create_policy(session: Session, car: models.Car) -> models.InsurancePolicy:
    today = date.today()
    start = today - timedelta(days=random.randint(0, 365))
    if random.random() < 0.5:
        end_date = start + timedelta(days=random.randint(30, 365))
        if end_date < today:
            # ensure some active ones
            end_date = today + timedelta(days=random.randint(15, 180))
    else:
        end_date = start + timedelta(days=random.randint(30, 365))
        if end_date > today:
            # force expired
            end_date = today - timedelta(days=random.randint(1, 30))

    policy = models.InsurancePolicy(
        car=car,
        provider=random.choice(
            ["AXA", "Allianz", "Zurich", "Generali", "StateFarm", "Liberty"]
        ),
        start_date=start,
        end_date=end_date,
        logged_expiry_at=None,
    )
    session.add(policy)
    return policy


def create_claim(session: Session, car: models.Car) -> models.Claim:
    today = date.today()
    claim_date = today - timedelta(days=random.randint(0, 720))
    amount = Decimal(random.randint(200, 5000)) + Decimal(random.randint(0, 99)) / 100
    claim = models.Claim(
        car=car,
        claim_date=claim_date,
        description=fake.sentence(nb_words=10),
        amount=amount,
    )
    session.add(claim)
    return claim


def purge_data(session: Session) -> None:
    """Delete existing rows in FK-safe order."""
    # Child tables first
    for model in (models.Claim, models.InsurancePolicy, models.Car, models.Owner):
        deleted = session.query(model).delete()
        print(f"Purged {deleted} rows from {model.__tablename__}")


# -------------- Main seeding routine --------------


def seed(
    owners: int,
    cars_per_owner: int,
    policies_per_car: int,
    claims_per_car: int,
    purge: bool,
) -> None:
    session = SESSION_LOCAL()
    try:
        if purge:
            purge_data(session)
            session.commit()
        print("Seeding data...")
        for _ in range(owners):
            owner = create_owner(session)
            for _ in range(cars_per_owner):
                car = create_car(session, owner)
                for _ in range(policies_per_car):
                    create_policy(session, car)
                for _ in range(claims_per_car):
                    create_claim(session, car)
        session.commit()
        print("Seed complete ✔")
    except Exception as exc:
        session.rollback()
        print(f"Error during seed, rolled back: {exc}")
        raise
    finally:
        session.close()


# -------------- CLI --------------


def parse_args():
    parser = argparse.ArgumentParser(description="Seed database with mock data")
    parser.add_argument("--owners", type=int, default=5, help="Number of owners")
    parser.add_argument("--cars-per-owner", type=int, default=2, help="Cars per owner")
    parser.add_argument(
        "--policies-per-car", type=int, default=1, help="Policies per car"
    )
    parser.add_argument("--claims-per-car", type=int, default=2, help="Claims per car")
    parser.add_argument(
        "--purge", action="store_true", help="Delete existing data first"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    seed(
        owners=args.owners,
        cars_per_owner=args.cars_per_owner,
        policies_per_car=args.policies_per_car,
        claims_per_car=args.claims_per_car,
        purge=args.purge,
    )


if __name__ == "__main__":
    main()
