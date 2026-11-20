from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TariffBase(BaseModel):
    category_id: int = Field(..., gt=0)
    hourly_rate: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)
    daily_rate: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)
    weekly_rate: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)
    free_km_per_day: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=2)
    extra_km_rate: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)
    extra_hour_rate: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)
    deposit_amount: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)
    effective_from: Optional[datetime] = None


class TariffCreate(TariffBase):
    pass


class TariffResponse(TariffBase):
    id: int
    is_active: bool
    effective_from: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
