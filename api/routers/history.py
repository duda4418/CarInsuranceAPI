from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import Car, InsurancePolicy, Claim
from typing import List, Dict, Any

history_router = APIRouter()

@history_router.get(
	"/cars/{car_id}/history",
	status_code=status.HTTP_200_OK,
	responses={
		200: {"description": "Chronological list of policies and claims for a car"},
		404: {"description": "Car not found"}
	}
)
def car_history(car_id: int, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
	car = db.query(Car).filter(Car.id == car_id).first()
	if not car:
		raise HTTPException(status_code=404, detail="Car not found")
	# Get all policies and claims for the car
	policies = db.query(InsurancePolicy).filter(InsurancePolicy.car_id == car_id).all()
	claims = db.query(Claim).filter(Claim.car_id == car_id).all()
	# Transform to unified dicts
	events = []
	for p in policies:
		events.append({
			"type": "POLICY",
			"policyId": p.id,
			"startDate": p.start_date.isoformat(),
			"endDate": p.end_date.isoformat() if p.end_date else None,
			"provider": p.provider
		})
	for c in claims:
		events.append({
			"type": "CLAIM",
			"claimId": c.id,
			"claimDate": c.claim_date.isoformat(),
			"amount": float(c.amount),
			"description": c.description
		})
	# Sort by date (startDate for policy, claimDate for claim)
	def event_date(e):
		return e.get("startDate") or e.get("claimDate")
	events.sort(key=event_date)
	return events