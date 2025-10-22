from fastapi import APIRouter, status, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.models import InsurancePolicy, Car
from api.schemas import InsurancePolicyCreate, InsurancePolicyRead

from db.session import get_db


policies_router = APIRouter()

@policies_router.post(
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

# GET /cars/{car_id}/insurance-valid?date=YYYY-MM-DD
