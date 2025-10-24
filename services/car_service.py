"""Car service: encapsulates Car CRUD and nested resource creation orchestration."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from api.schemas import CarCreate
from core.logging import get_logger
from db.models import Car, Owner
from services.exceptions import NotFoundError, ValidationError

log = get_logger()


def list_cars(db: Session) -> list[Car]:
    """List all cars with their owners."""
    return db.query(Car).options(joinedload(Car.owner)).all()


def get_car(db: Session, car_id: int) -> Car:
    """Get a car by ID, including owner."""
    car = db.query(Car).options(joinedload(Car.owner)).filter(Car.id == car_id).first()
    if not car:
        raise NotFoundError("Car", car_id)
    return car


def create_car(db: Session, data: CarCreate) -> Car:
    """Create a new car and assign to owner."""
    owner = db.query(Owner).filter(Owner.id == data.owner_id).first()
    if not owner:
        raise NotFoundError("Owner", data.owner_id)
    existing = db.query(Car).filter(Car.vin == data.vin).first()
    if existing:
        raise ValidationError(f"VIN '{data.vin}' already exists")
    car = Car(**data.model_dump())
    db.add(car)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        if isinstance(e, IntegrityError):
            raise ValidationError(f"VIN '{data.vin}' already exists")
        raise
    db.refresh(car)
    log.info("car_created", carId=car.id, ownerId=car.owner_id, vin=car.vin)
    return car


def update_car(db: Session, car_id: int, data: CarCreate) -> Car:
    """Update an existing car's details."""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise NotFoundError("Car", car_id)
    owner = db.query(Owner).filter(Owner.id == data.owner_id).first()
    if not owner:
        raise NotFoundError("Owner", data.owner_id)
    if data.vin != car.vin:
        existing_vin = db.query(Car).filter(Car.vin == data.vin).first()
        if existing_vin:
            raise ValidationError(f"VIN '{data.vin}' already exists")
    for key, value in data.model_dump().items():
        setattr(car, key, value)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        if isinstance(e, IntegrityError):
            raise ValidationError("Update violates data integrity constraints")
        raise
    db.refresh(car)
    log.info("car_updated", carId=car.id, ownerId=car.owner_id, vin=car.vin)
    return car


def delete_car(db: Session, car_id: int) -> None:
    """Delete a car by ID."""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise NotFoundError("Car", car_id)
    db.delete(car)
    db.commit()
    log.info("car_deleted", carId=car_id)
