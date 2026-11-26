from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


# Branch Schemas
class BranchCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=50)
    address: str = Field(..., min_length=5, max_length=255)
    contact_no: str = Field(..., min_length=8, max_length=20)


class BranchUpdate(BaseModel):
    address: Optional[str] = None
    contact_no: Optional[str] = None


class BranchResponse(BaseModel):
    id: int
    name: str
    city: str
    address: str
    contact_no: str
    is_active: bool

    class Config:
        from_attributes = True


# Vehicle Schemas
class VehicleCreate(BaseModel):
    registration_no: str = Field(..., min_length=3, max_length=50)
    category_id: int
    branch_id: int
    make: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    fuel_type: str
    transmission: str
    odometer_km: Decimal = Field(default=Decimal("0.0"), ge=0)


class VehicleStatusUpdate(BaseModel):
    status: str  # AVAILABLE, BOOKED, UNDER_MAINTENANCE, RETIRED
    odometer_km: Optional[Decimal] = None


class VehicleResponse(BaseModel):
    id: int
    registration_no: str
    category_id: int
    branch_id: int
    make: str
    model: str
    fuel_type: str
    transmission: str
    odometer_km: Decimal
    status: str
    is_active: bool

    class Config:
        from_attributes = True

