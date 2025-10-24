"""History aggregation service."""

from sqlalchemy.orm import Session

from db.models import Car, Claim, InsurancePolicy
from services.exceptions import NotFoundError


def get_car_history(db: Session, car_id: int) -> list[dict]:
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise NotFoundError("Car", car_id)

    policies = db.query(InsurancePolicy).filter(InsurancePolicy.car_id == car_id).all()
    claims = db.query(Claim).filter(Claim.car_id == car_id).all()
    events: list[dict] = []

    for p in policies:
        events.append(
            {
                "type": "POLICY",
                "policyId": p.id,
                "startDate": p.start_date.isoformat(),
                "endDate": p.end_date.isoformat() if p.end_date else None,
                "provider": p.provider,
            }
        )

    for c in claims:
        events.append(
            {
                "type": "CLAIM",
                "claimId": c.id,
                "claimDate": c.claim_date.isoformat(),
                "amount": float(c.amount),
                "description": c.description,
            }
        )

    def event_date(e: dict):
        return e.get("startDate") or e.get("claimDate")

    events.sort(key=event_date)

    return events
