# --- Standard Library Imports ---
from typing import Dict, Any, List
from datetime import datetime
# --- Third Party Imports ---
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session, joinedload
# --- Project Imports ---
from db.models import Car, InsurancePolicy, Claim
from db.session import get_db
from api.schemas import CarRead, CarCreate, InsurancePolicyCreate, InsurancePolicyRead, ClaimCreate, ClaimRead

from services.policy_service import create_policy as svc_create_policy
from services.claim_service import create_claim as svc_create_claim
from services.validity_service import is_insurance_valid
from services.history_service import get_car_history
from services.exceptions import NotFoundError, ValidationError
from core.logging import get_logger

log = get_logger()


cars_router = APIRouter()

@cars_router.get(
    "/cars",
    response_model=List[CarRead],
    status_code=status.HTTP_200_OK,
    responses={200: {"status": "ok"}}
)
def list_cars(db: Session = Depends(get_db)):
    car_list = db.query(Car).options(joinedload(Car.owner)).all()

    return car_list


@cars_router.get(
    "/cars/{car_id}",
    response_model=CarRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Car found"},
        404: {"description": "Car not found"}
    }
)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = (db.query(Car).options(joinedload(Car.owner)).filter(Car.id == car_id).first())

    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")

    return car


@cars_router.post(
    "/cars",
    response_model=CarRead,
    status_code=status.HTTP_201_CREATED,
    responses={201: {"description": "Car created"}, 400: {"description": "Invalid input"}}
)
def create_car(car: CarCreate, db: Session = Depends(get_db), response: Response = None):
    db_car = Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)

    if response is not None:
        response.headers["Location"] = f"/api/cars/{db_car.id}"

    return db_car


@cars_router.put(
    "/cars/{car_id}",
    response_model=CarRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Car updated"},
        404: {"description": "Car not found"},
        400: {"description": "Invalid input"}
    }
)
def update_car(car_id: int, car: CarCreate, db: Session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.id == car_id).first()

    if not db_car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")

    for key, value in car.dict().items():
        setattr(db_car, key, value)
    db.commit()
    db.refresh(db_car)

    return db_car


@cars_router.delete(
    "/cars/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Car deleted"},
        404: {"description": "Car not found"}
    }
)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.id == car_id).first()

    if not db_car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")

    db.delete(db_car)
    db.commit()

    return None


@cars_router.post(
    "/cars/{car_id}/policies",
    response_model=InsurancePolicyRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Policy created"},
        400: {"description": "Invalid input or date logic"},
        404: {"description": "Car not found"}
    }
)
def create_policy_for_car(car_id: int, policy: InsurancePolicyCreate, db: Session = Depends(get_db)):
    try:
        created = svc_create_policy(db, car_id, policy)
        log.info("policy_created", policyId=created.id, carId=car_id, provider=created.provider)
        return created
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    except ValidationError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@cars_router.post(
    "/cars/{car_id}/claims",
    response_model=ClaimRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Claim created"},
        400: {"description": "Invalid input"},
        404: {"description": "Car not found"}
    }
)
def create_claims(car_id: int, claim: ClaimCreate, db: Session = Depends(get_db), response: Response = None):
    try:
        created = svc_create_claim(db, car_id, claim)
        log.info("claim_created", claimId=created.id, carId=car_id, amount=float(created.amount))
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Car not found")
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    if response is not None:
        response.headers["Location"] = f"/api/cars/{car_id}/claims/{created.id}"
    return created


@cars_router.get(
    "/cars/{car_id}/insurance-valid",
    status_code=200,
    responses={
        200: {"description": "Insurance validity for car and date"},
        400: {"description": "Invalid date format or out of range"},
        404: {"description": "Car not found"}
    }
)
def insurance_valid(
    car_id: int,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    try:
        valid = is_insurance_valid(db, car_id, date)
        return {"carId": car_id, "date": date, "valid": valid}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Car not found")
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@cars_router.get(
    "/cars/{car_id}/history",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Chronological list of policies and claims for a car"},
        404: {"description": "Car not found"}
    }
)
def car_history(car_id: int, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    try:
        return get_car_history(db, car_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Car not found")



