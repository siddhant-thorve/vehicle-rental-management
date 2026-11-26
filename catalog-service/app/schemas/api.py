from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    seating_capacity: int = Field(..., gt=0)


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    seating_capacity: int
    is_active: bool

    class Config:
        from_attributes = True


class TariffCreate(BaseModel):
    category_id: int
    hourly_rate: Decimal = Field(..., gt=0)
    daily_rate: Decimal = Field(..., gt=0)
    weekly_rate: Decimal = Field(..., gt=0)
    free_km_per_day: Decimal = Field(..., gt=0)
    extra_km_rate: Decimal = Field(..., gt=0)
    extra_hour_rate: Decimal = Field(..., gt=0)
    deposit_amount: Decimal = Field(..., ge=0)


class TariffResponse(BaseModel):
    id: int
    category_id: int
    hourly_rate: Decimal
    daily_rate: Decimal
    weekly_rate: Decimal
    free_km_per_day: Decimal
    extra_km_rate: Decimal
    extra_hour_rate: Decimal
    deposit_amount: Decimal
    effective_from: datetime

    class Config:
        from_attributes = True
