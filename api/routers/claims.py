from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from api.schemas import ClaimCreate, ClaimRead
from db.session import get_db
from db.models import Car, Claim

claims_router = APIRouter()


@claims_router.get(
	"/claims",
	response_model=List[ClaimRead],
	status_code=status.HTTP_200_OK,
	responses={200: {"description": "List of claims"}}
)
def list_claims(db: Session = Depends(get_db)):
	return db.query(Claim).all()


@claims_router.get(
	"/claims/{claim_id}",
	response_model=ClaimRead,
	status_code=status.HTTP_200_OK,
	responses={
		200: {"description": "Claim retrieved"},
		404: {"description": "Claim not found"}
	}
)
def get_claim(claim_id: int, db: Session = Depends(get_db)):
	claim = db.query(Claim).filter(Claim.id == claim_id).first()

	if not claim:
		raise HTTPException(status_code=404, detail="Claim not found")

	return claim


@claims_router.post(
	"/claims",
	response_model=ClaimRead,
	status_code=status.HTTP_201_CREATED,
	responses={
		201: {"description": "Claim created"},
		400: {"description": "Invalid input"},
		404: {"description": "Car not found"}
	}
)
def create_claim(payload: ClaimCreate, db: Session = Depends(get_db), response: Response = None):
	car = db.query(Car).filter(Car.id == payload.car_id).first()

	if not car:
		raise HTTPException(status_code=404, detail="Car not found")

	if not payload.description or not payload.description.strip():
		raise HTTPException(status_code=400, detail="Description must not be empty")

	if payload.amount is None or payload.amount <= 0:
		raise HTTPException(status_code=400, detail="Amount must be greater than 0")

	claim = Claim(
		car_id=payload.car_id,
		claim_date=payload.claim_date,
		description=payload.description,
		amount=payload.amount
	)
	db.add(claim)
	db.commit()
	db.refresh(claim)

	if response is not None:
		response.headers["Location"] = f"/api/claims/{claim.id}"

	return claim


@claims_router.put(
	"/claims/{claim_id}",
	response_model=ClaimRead,
	status_code=status.HTTP_200_OK,
	responses={
		200: {"description": "Claim updated"},
		404: {"description": "Claim not found"},
		400: {"description": "Invalid input"}
	}
)
def update_claim(claim_id: int, payload: ClaimCreate, db: Session = Depends(get_db)):
	claim = db.query(Claim).filter(Claim.id == claim_id).first()

	if not claim:
		raise HTTPException(status_code=404, detail="Claim not found")

	# validations
	if not payload.description or not payload.description.strip():
		raise HTTPException(status_code=400, detail="Description must not be empty")

	if payload.amount is None or payload.amount <= 0:
		raise HTTPException(status_code=400, detail="Amount must be greater than 0")

	# car change
	if payload.car_id != claim.car_id:
		car = db.query(Car).filter(Car.id == payload.car_id).first()
		if not car:
			raise HTTPException(status_code=404, detail="New car not found")
		claim.car_id = payload.car_id

	claim.claim_date = payload.claim_date
	claim.description = payload.description
	claim.amount = payload.amount
	db.commit()
	db.refresh(claim)

	return claim


@claims_router.delete(
	"/claims/{claim_id}",
	status_code=status.HTTP_204_NO_CONTENT,
	responses={
		204: {"description": "Claim deleted"},
		404: {"description": "Claim not found"}
	}
)
def delete_claim(claim_id: int, db: Session = Depends(get_db)):
	claim = db.query(Claim).filter(Claim.id == claim_id).first()

	if not claim:
		raise HTTPException(status_code=404, detail="Claim not found")

	db.delete(claim)
	db.commit()
	
	return None

