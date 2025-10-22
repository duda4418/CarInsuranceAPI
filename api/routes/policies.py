from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import InsurancePolicy, Car
from datetime import datetime

policies_router = APIRouter()

@policies_router.get(
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
    # Validate car exists
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    # Validate date format and range
    try:
        d = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    if d.year < 1900 or d.year > 2100:
        raise HTTPException(status_code=400, detail="Date out of range")
    # Check for active policy
    valid = db.query(InsurancePolicy).filter(
        InsurancePolicy.car_id == car_id,
        InsurancePolicy.start_date <= d,
        InsurancePolicy.end_date >= d
    ).first() is not None
    return {"carId": car_id, "date": date, "valid": valid}
