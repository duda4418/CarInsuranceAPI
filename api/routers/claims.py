from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session


from api.schemas import ClaimCreate, ClaimRead
from db.session import get_db
from db.models import Car, Claim
from fastapi import HTTPException, Response

claims_router = APIRouter()

@claims_router.post("/cars/{car_id}/claims",
                    response_model=ClaimRead,
                    status_code=status.HTTP_201_CREATED,
                    responses={
                        201: {"description": "Claim created"},
                        400: {"description": "Invalid input"},
                        404: {"description": "Car not found"}
                    })
def create_claims(car_id: int, claim: ClaimCreate, db: Session = Depends(get_db), response: Response = None):
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Validation
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

    #Location Header
    if response is not None:
        response.headers["Location"] = f"/api/cars/{car_id}/claims/{db_claim.id}"

    return db_claim
