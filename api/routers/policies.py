from fastapi import APIRouter, status, Depends, Response
from sqlalchemy.orm import Session
from typing import List

from db.models import InsurancePolicy, Car
from api.schemas import InsurancePolicyCreate, InsurancePolicyRead
from db.session import get_db
from services.exceptions import NotFoundError
from core.logging import get_logger
from services.policy_service import (
	list_policies as svc_list_policies,
	get_policy_by_id as svc_get_policy_by_id,
	create_policy as svc_create_policy,
	update_policy as svc_update_policy,
	delete_policy as svc_delete_policy,
)

log = get_logger()

policies_router = APIRouter()


@policies_router.get(
	"/policies",
	response_model=List[InsurancePolicyRead],
	status_code=status.HTTP_200_OK,
	responses={
		200: {"description": "List of policies"},
		422: {"description": "Validation error in query/path"}
	}
)
def list_policies(db: Session = Depends(get_db)):
	return svc_list_policies(db)


@policies_router.get(
	"/policies/{policy_id}",
	response_model=InsurancePolicyRead,
	status_code=status.HTTP_200_OK,
	responses={
		200: {"description": "Policy retrieved"},
		404: {"description": "Policy not found"},
		422: {"description": "Invalid path parameter"}
	}
)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
	policy = svc_get_policy_by_id(db, policy_id)
	if not policy:
		raise NotFoundError("Policy", policy_id)
	return policy


@policies_router.post(
	"/policies",
	response_model=InsurancePolicyRead,
	status_code=status.HTTP_201_CREATED,
	responses={
		201: {"description": "Policy created"},
		400: {"description": "Domain validation error (date logic)"},
		404: {"description": "Car not found"},
		422: {"description": "Request body validation error"}
	}
)
def create_policy(payload: InsurancePolicyCreate, db: Session = Depends(get_db), response: Response = None):
	policy = svc_create_policy(db, payload.car_id, payload)
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
		422: {"description": "Request body validation error"}
	}
)
def update_policy(policy_id: int, payload: InsurancePolicyCreate, db: Session = Depends(get_db)):
	policy = svc_get_policy_by_id(db, policy_id)
	if not policy:
		raise NotFoundError("Policy", policy_id)
	updated = svc_update_policy(db, policy, payload)
	log.info("policy_updated", policyId=updated.id, carId=updated.car_id, provider=updated.provider)
	return updated


@policies_router.delete(
	"/policies/{policy_id}",
	status_code=status.HTTP_204_NO_CONTENT,
	responses={
		204: {"description": "Policy deleted"},
		404: {"description": "Policy not found"},
		422: {"description": "Invalid path parameter"}
	}
)
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
	policy = svc_get_policy_by_id(db, policy_id)
	if not policy:
		raise NotFoundError("Policy", policy_id)
	svc_delete_policy(db, policy)
	log.info("policy_deleted", policyId=policy.id, carId=policy.car_id)
	return None
