from typing import Dict, Any, List

from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.orm import Session

from db.session import get_db
from api.schemas import CarRead, CarCreate, InsurancePolicyCreate, InsurancePolicyCreateNested, InsurancePolicyRead, ClaimCreate, ClaimCreateNested, ClaimRead, InsuranceValidityResponse

from services.car_service import (
    list_cars as svc_list_cars,
    get_car as svc_get_car,
    create_car as svc_create_car,
    update_car as svc_update_car,
    delete_car as svc_delete_car,
)
from services.policy_service import create_policy as svc_create_policy
from services.claim_service import create_claim as svc_create_claim
from services.validity_service import is_insurance_valid
from services.history_service import get_car_history

cars_router = APIRouter()


@cars_router.get(
    "/cars",
    response_model=List[CarRead],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of cars"},
        422: {"description": "Validation error in query/path"}
    }
)
def list_cars(db: Session = Depends(get_db)):
    return svc_list_cars(db)


@cars_router.get(
    "/cars/{car_id}",
    response_model=CarRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Car found"},
        404: {"description": "Car not found"},
        422: {"description": "Invalid path parameter"}
    }
)
def get_car(car_id: int, db: Session = Depends(get_db)):
    return svc_get_car(db, car_id)


@cars_router.post(
    "/cars",
    response_model=CarRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Car created"},
        400: {"description": "Domain validation error"},
        404: {"description": "Owner not found"},
        422: {"description": "Request body validation error"}
    }
)
def create_car(car: CarCreate, db: Session = Depends(get_db), response: Response = None):
    created = svc_create_car(db, car)
    if response is not None:
        response.headers["Location"] = f"/api/cars/{created.id}"
    return created


@cars_router.put(
    "/cars/{car_id}",
    response_model=CarRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Car updated"},
        404: {"description": "Car not found"},
        422: {"description": "Request body validation error"}
    }
)
def update_car(car_id: int, car: CarCreate, db: Session = Depends(get_db)):
    return svc_update_car(db, car_id, car)


@cars_router.delete(
    "/cars/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Car deleted"},
        404: {"description": "Car not found"},
        422: {"description": "Invalid path parameter"}
    }
)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    svc_delete_car(db, car_id)
    return None


@cars_router.post(
    "/cars/{car_id}/policies",
    response_model=InsurancePolicyRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Policy created"},
        400: {"description": "Domain validation error (date logic)"},
        404: {"description": "Car not found"},
        422: {"description": "Request body validation error"}
    }
)
def create_policy_for_car(car_id: int, policy: InsurancePolicyCreateNested, db: Session = Depends(get_db), response: Response = None):
    created = svc_create_policy(db, car_id, policy)
    if response is not None:
        response.headers["Location"] = f"/api/policies/{created.id}"
    return created


@cars_router.post(
    "/cars/{car_id}/claims",
    response_model=ClaimRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Claim created"},
        400: {"description": "Domain validation error"},
        404: {"description": "Car not found"},
        422: {"description": "Request body validation error"}
    }
)
def create_claims(car_id: int, claim: ClaimCreateNested, db: Session = Depends(get_db), response: Response = None):
    created = svc_create_claim(db, car_id, claim)
    if response is not None:
        response.headers["Location"] = f"/api/cars/{car_id}/claims/{created.id}"
    return created


@cars_router.get(
    "/cars/{car_id}/insurance-valid",
    status_code=200,
    response_model=InsuranceValidityResponse,
    responses={
        200: {"description": "Insurance validity for car and date"},
        400: {"description": "Domain validation error (date logic)"},
        404: {"description": "Car not found"},
        422: {"description": "Query parameter validation error"}
    }
)
def insurance_valid(
    car_id: int,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    valid = is_insurance_valid(db, car_id, date)
    return InsuranceValidityResponse(car_id=car_id, date=date, valid=valid)


@cars_router.get(
    "/cars/{car_id}/history",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Chronological list of policies and claims for a car"},
        404: {"description": "Car not found"}
    }
)
def car_history(car_id: int, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    return get_car_history(db, car_id)



