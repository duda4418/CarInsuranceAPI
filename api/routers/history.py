from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import Car, InsurancePolicy, Claim
from typing import List, Dict, Any

history_router = APIRouter()

"""History router.

Provides a read-only aggregation view (car timelines). CRUD (create/update/delete) is
not appropriate because the underlying data comes from policies and claims resources.
We expose only GET endpoints here by design.
"""

