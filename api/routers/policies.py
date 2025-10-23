from fastapi import APIRouter, status, Depends, Response
from sqlalchemy.orm import Session
from typing import List

from db.models import InsurancePolicy, Car
from api.schemas import InsurancePolicyCreate, InsurancePolicyRead
from db.session import get_db
from services.exceptions import NotFoundError, ValidationError
from core.logging import get_logger

log = get_logger()

policies_router = APIRouter()


@policies_router.get(
	"/policies",
	response_model=List[InsurancePolicyRead],
	status_code=status.HTTP_200_OK,
	responses={200: {"description": "List of policies"}}
)
def list_policies(db: Session = Depends(get_db)):
	return db.query(InsurancePolicy).all()


@policies_router.get(
	"/policies/{policy_id}",
	response_model=InsurancePolicyRead,
	status_code=status.HTTP_200_OK,
	responses={
		200: {"description": "Policy retrieved"},
		404: {"description": "Policy not found"}
	}
)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
	policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
	if not policy:
		raise NotFoundError("Policy", policy_id)
	return policy


@policies_router.post(
	"/policies",
	response_model=InsurancePolicyRead,
	status_code=status.HTTP_201_CREATED,
	responses={
		201: {"description": "Policy created"},
		400: {"description": "Invalid input"},
		404: {"description": "Car not found"}
	}
)
def create_policy(payload: InsurancePolicyCreate, db: Session = Depends(get_db), response: Response = None):
	car = db.query(Car).filter(Car.id == payload.car_id).first()
	if not car:
		raise NotFoundError("Car", payload.car_id)
	# Date ordering & range now enforced by Pydantic validators; no manual check needed.
	policy = InsurancePolicy(
		car_id=payload.car_id,
		provider=payload.provider,
		start_date=payload.start_date,
		end_date=payload.end_date,
		logged_expiry_at=payload.logged_expiry_at
	)
	db.add(policy)
	db.commit()
	db.refresh(policy)
	if response is not None:
		response.headers["Location"] = f"/api/policies/{policy.id}"
	log.info("policy_created", policyId=policy.id, carId=policy.car_id, provider=policy.provider)
	return policy


@policies_router.put(
	"/policies/{policy_id}",
	response_model=InsurancePolicyRead,
	status_code=status.HTTP_200_OK,
	responses={
		200: {"description": "Policy updated"},
		404: {"description": "Policy not found"},
		400: {"description": "Invalid input"}
	}
)
def update_policy(policy_id: int, payload: InsurancePolicyCreate, db: Session = Depends(get_db)):
	policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
	if not policy:
		raise NotFoundError("Policy", policy_id)
	# Pydantic validators handle date logic.
	if payload.car_id != policy.car_id:
		car = db.query(Car).filter(Car.id == payload.car_id).first()
		if not car:
			raise NotFoundError("Car", payload.car_id)
	policy.car_id = payload.car_id
	policy.provider = payload.provider
	policy.start_date = payload.start_date
	policy.end_date = payload.end_date
	policy.logged_expiry_at = payload.logged_expiry_at
	db.commit()
	db.refresh(policy)
	log.info("policy_updated", policyId=policy.id, carId=policy.car_id, provider=policy.provider)
	return policy


@policies_router.delete(
	"/policies/{policy_id}",
	status_code=status.HTTP_204_NO_CONTENT,
	responses={
		204: {"description": "Policy deleted"},
		404: {"description": "Policy not found"}
	}
)
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
	policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
	if not policy:
		raise NotFoundError("Policy", policy_id)
	db.delete(policy)
	db.commit()
	log.info("policy_deleted", policyId=policy.id, carId=policy.car_id)
	return None
