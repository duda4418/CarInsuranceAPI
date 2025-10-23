from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from core.config import CamelModel


# Owner Models
class OwnerCreate(CamelModel):
	name: str
	email: Optional[str] = None

class OwnerRead(CamelModel):
	id: int
	name: str
	email: Optional[str] = None
	model_config = {
		**CamelModel.model_config,
		'from_attributes': True,
	}


# Car Models
class CarCreate(CamelModel):
	vin: str
	make: Optional[str] = None
	model: Optional[str] = None
	year_of_manufacture: Optional[int] = None
	owner_id: int

class CarRead(CamelModel):
	id: int
	vin: str
	make: Optional[str] = None
	model: Optional[str] = None
	year_of_manufacture: Optional[int] = None
	owner: OwnerRead
	model_config = {
		**CamelModel.model_config,
		'from_attributes': True,
	}


# Insurance Policy Models
class InsurancePolicyCreate(CamelModel):
	car_id: int
	provider: Optional[str] = None
	start_date: date
	end_date: date
	logged_expiry_at: Optional[datetime] = None

class InsurancePolicyRead(CamelModel):
	id: int
	car_id: int
	provider: Optional[str] = None
	start_date: date
	end_date: date
	logged_expiry_at: Optional[datetime] = None
	model_config = {
		**CamelModel.model_config,
		'from_attributes': True,
	}


# Claim Models
class ClaimCreate(CamelModel):
	car_id: int
	claim_date: date
	description: str
	amount: Decimal

class ClaimRead(CamelModel):
	id: int
	car_id: int
	claim_date: date
	description: str
	amount: Decimal
	created_at: datetime
	model_config = {
		**CamelModel.model_config,
		'from_attributes': True,
	}

