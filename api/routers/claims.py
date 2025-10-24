from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from typing import List

from api.schemas import ClaimCreate, ClaimRead
from db.session import get_db
from services.exceptions import NotFoundError
from db.models import Claim
from services.claim_service import (
	list_claims as svc_list_claims,
	get_claim_by_id as svc_get_claim_by_id,
	create_claim as svc_create_claim,
	update_claim as svc_update_claim,
	delete_claim as svc_delete_claim,
)

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
	return svc_list_claims(db)


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
	claim = svc_get_claim_by_id(db, claim_id)
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
	claim = svc_create_claim(db, payload.car_id, payload)
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
		422: {"description": "Request body validation error"}
	}
)
def update_claim(claim_id: int, payload: ClaimCreate, db: Session = Depends(get_db)):
	claim = svc_get_claim_by_id(db, claim_id)
	if not claim:
		raise NotFoundError("Claim", claim_id)
	updated = svc_update_claim(db, claim, payload)
	return updated


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
	claim = svc_get_claim_by_id(db, claim_id)
	if not claim:
		raise NotFoundError("Claim", claim_id)
	svc_delete_claim(db, claim)
	return None

