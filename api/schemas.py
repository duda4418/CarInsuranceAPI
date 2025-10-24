from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import field_validator
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
# Used for top-level /api/policies endpoints (requires car_id)
class InsurancePolicyCreate(CamelModel):
	car_id: int
	provider: Optional[str] = None
	start_date: date
	end_date: date
	logged_expiry_at: Optional[datetime] = None

# Used for nested /cars/{car_id}/policies endpoints (no car_id in body)
class InsurancePolicyCreateNested(CamelModel):
	provider: Optional[str] = None
	start_date: date
	end_date: date
	logged_expiry_at: Optional[datetime] = None

	@field_validator("end_date")
	def validate_end_date(cls, v: date, info):
		start = info.data.get("start_date")
		if start and v < start:
			raise ValueError("endDate must be >= startDate")
		if v.year < 1900 or v.year > 2100:
			raise ValueError("endDate out of allowed range (1900-2100)")
		return v

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

class InsuranceValidityResponse(CamelModel):
	car_id: int
	date: str
	valid: bool


# Claim Models
# Used for top-level /api/claims endpoints (requires car_id)
class ClaimCreate(CamelModel):
	car_id: int
	claim_date: date
	description: str
	amount: Decimal

# Used for nested /cars/{car_id}/claims endpoints (no car_id in body)
class ClaimCreateNested(CamelModel):
	claim_date: date
	description: str
	amount: Decimal

	@field_validator("amount")
	def validate_amount(cls, v: Decimal):
		if v <= 0:
			raise ValueError("amount must be > 0")
		return v

	@field_validator("description")
	def validate_description(cls, v: str):
		if not v or not v.strip():
			raise ValueError("description must not be empty")
		return v

	@field_validator("claim_date")
	def validate_claim_date(cls, v: date):
		if v.year < 1900 or v.year > 2100:
			raise ValueError("claimDate out of allowed range (1900-2100)")
		return v

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


class HealthRead(CamelModel):
    status: str

