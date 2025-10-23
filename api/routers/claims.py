from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from typing import List

from api.schemas import ClaimCreate, ClaimRead
from db.session import get_db
from services.exceptions import NotFoundError, ValidationError
from db.models import Car, Claim
from core.logging import get_logger

log = get_logger()

claims_router = APIRouter()


@claims_router.get(
	"/claims",
	response_model=List[ClaimRead],
	status_code=status.HTTP_200_OK,
	responses={
		200: {"description": "List of claims"},
		422: {"description": "Validation error in query/path"}
	}
)
def list_claims(db: Session = Depends(get_db)):
	return db.query(Claim).all()


@claims_router.get(
	"/claims/{claim_id}",
	response_model=ClaimRead,
	status_code=status.HTTP_200_OK,
	responses={
		200: {"description": "Claim retrieved"},
		404: {"description": "Claim not found"},
		422: {"description": "Invalid path parameter"}
	}
)
def get_claim(claim_id: int, db: Session = Depends(get_db)):
	claim = db.query(Claim).filter(Claim.id == claim_id).first()
	if not claim:
		raise NotFoundError("Claim", claim_id)
	return claim


@claims_router.post(
	"/claims",
	response_model=ClaimRead,
	status_code=status.HTTP_201_CREATED,
	responses={
		201: {"description": "Claim created"},
		400: {"description": "Domain validation error"},
		404: {"description": "Car not found"},
		422: {"description": "Request body validation error"}
	}
)
def create_claim(payload: ClaimCreate, db: Session = Depends(get_db), response: Response = None):
	car = db.query(Car).filter(Car.id == payload.car_id).first()
	if not car:
		raise NotFoundError("Car", payload.car_id)
	# Pydantic validators enforce description/amount rules.
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
	log.info("claim_created", claimId=claim.id, carId=claim.car_id, amount=float(claim.amount))
	return claim


@claims_router.put(
	"/claims/{claim_id}",
	response_model=ClaimRead,
	status_code=status.HTTP_200_OK,
	responses={
		200: {"description": "Claim updated"},
		404: {"description": "Claim not found"},
		422: {"description": "Request body validation error"}
	}
)
def update_claim(claim_id: int, payload: ClaimCreate, db: Session = Depends(get_db)):
	claim = db.query(Claim).filter(Claim.id == claim_id).first()
	if not claim:
		raise NotFoundError("Claim", claim_id)
	if payload.car_id != claim.car_id:
		car = db.query(Car).filter(Car.id == payload.car_id).first()
		if not car:
			raise NotFoundError("Car", payload.car_id)
		claim.car_id = payload.car_id
	claim.claim_date = payload.claim_date
	claim.description = payload.description
	claim.amount = payload.amount
	db.commit()
	db.refresh(claim)
	log.info("claim_updated", claimId=claim.id, carId=claim.car_id, amount=float(claim.amount))
	return claim


@claims_router.delete(
	"/claims/{claim_id}",
	status_code=status.HTTP_204_NO_CONTENT,
	responses={
		204: {"description": "Claim deleted"},
		404: {"description": "Claim not found"},
		422: {"description": "Invalid path parameter"}
	}
)
def delete_claim(claim_id: int, db: Session = Depends(get_db)):
	claim = db.query(Claim).filter(Claim.id == claim_id).first()
	if not claim:
		raise NotFoundError("Claim", claim_id)
	db.delete(claim)
	db.commit()
	log.info("claim_deleted", claimId=claim.id, carId=claim.car_id)
	return None

