
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

class OwnerBase(BaseModel):
	name: str
	email: Optional[str] = None

class OwnerCreate(OwnerBase):
	pass

class OwnerRead(BaseModel):
	id: int
	name: str
	email: Optional[str] = None
	class Config:
		from_attributes = True
		ser_json_order = True

class CarBase(BaseModel):
	id: int
	vin: str
	make: Optional[str] = None
	model: Optional[str] = None
	year_of_manufacture: Optional[int] = None
	owner: OwnerRead = None

class CarCreate(CarBase):
	owner_id: int

class CarRead(BaseModel):
	id: int
	vin: str
	make: Optional[str] = None
	model: Optional[str] = None
	year_of_manufacture: Optional[int] = None
	owner: OwnerRead
	class Config:
		from_attributes = True

class InsurancePolicyBase(BaseModel):
	provider: Optional[str] = None
	start_date: date
	end_date: date
	logged_expiry_at: Optional[datetime] = None

class InsurancePolicyCreate(InsurancePolicyBase):
	pass

class InsurancePolicyRead(InsurancePolicyBase):
	id: int
	car_id: int
	class Config:
		from_attributes = True

class ClaimBase(BaseModel):
	claim_date: date
	description: str
	amount: Decimal

class ClaimCreate(ClaimBase):
	car_id: int

class ClaimRead(ClaimBase):
	id: int
	car_id: int
	created_at: datetime
	class Config:
		from_attributes = True

