from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from fastapi import status

from db.session import get_db

from db.models import InsurancePolicy
from api.schemas import InsurancePolicyCreate, InsurancePolicyRead
from db.models import Car
from api.schemas import CarRead, CarCreate
from sqlalchemy.orm import joinedload


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

# @cars_router.post(
#     "/cars",
#     response_model=CarRead,
#     status_code=status.HTTP_201_CREATED,
#     responses={201: {"description": "Car created"}, 400: {"description": "Invalid input"}}
# )
# def create_car(car: CarCreate, db: Session = Depends(get_db)):
#     db_car = Car(**car.dict())
#     db.add(db_car)
#     db.commit()
#     db.refresh(db_car)
#     return db_car


# @cars_router.put(
#     "/cars/{car_id}",
#     response_model=CarRead,
#     status_code=status.HTTP_200_OK,
#     responses={
#         200: {"description": "Car updated"},
#         404: {"description": "Car not found"},
#         400: {"description": "Invalid input"}
#     }
# )
# def update_car(car_id: int, car: CarCreate, db: Session = Depends(get_db)):
#     db_car = db.query(Car).filter(Car.id == car_id).first()
#     if not db_car:
#         from fastapi import HTTPException
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
#     for key, value in car.dict().items():
#         setattr(db_car, key, value)
#     db.commit()
#     db.refresh(db_car)
#     return db_car


# @cars_router.delete(
#     "/cars/{car_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     responses={
#         204: {"description": "Car deleted"},
#         404: {"description": "Car not found"}
#     }
# )
# def delete_car(car_id: int, db: Session = Depends(get_db)):
#     db_car = db.query(Car).filter(Car.id == car_id).first()
#     if not db_car:
#         from fastapi import HTTPException
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
#     db.delete(db_car)
#     db.commit()
#     return None
