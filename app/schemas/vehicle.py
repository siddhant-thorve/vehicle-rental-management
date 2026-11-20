from datetime import datetime
from enum import Enum
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    RETIRED = "RETIRED"


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    seating_capacity: int = Field(..., ge=1, le=50)


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleBase(BaseModel):
    registration_no: str = Field(..., min_length=3, max_length=50)
    category_id: int = Field(..., gt=0)
    branch_id: int = Field(..., gt=0)
    make: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    fuel_type: str = Field(..., min_length=2, max_length=50)
    transmission: str = Field(..., min_length=2, max_length=50)
    odometer_km: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int
    status: VehicleStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
