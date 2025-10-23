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
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")

    if policy.end_date is None or policy.end_date < policy.start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be present and >= start_date")

    db_policy = InsurancePolicy(
        car_id=car_id,
        provider=policy.provider,
        start_date=policy.start_date,
        end_date=policy.end_date,
        logged_expiry_at=policy.logged_expiry_at
    )
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)

    return db_policy


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
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    if not claim.description or not claim.description.strip():
        raise HTTPException(status_code=400, detail="Description must not be empty")

    if claim.amount is None or claim.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    db_claim = Claim(
        car_id=car_id,
        claim_date=claim.claim_date,
        description=claim.description,
        amount=claim.amount
    )
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)

    if response is not None:
        response.headers["Location"] = f"/api/cars/{car_id}/claims/{db_claim.id}"

    return db_claim


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
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    try:
        d = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    if d.year < 1900 or d.year > 2100:
        raise HTTPException(status_code=400, detail="Date out of range")

    valid = db.query(InsurancePolicy).filter(
        InsurancePolicy.car_id == car_id,
        InsurancePolicy.start_date <= d,
        InsurancePolicy.end_date >= d
    ).first() is not None

    return {"carId": car_id, "date": date, "valid": valid}


@cars_router.get(
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



