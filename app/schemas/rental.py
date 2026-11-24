from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PickupRequest(BaseModel):
    odometer_out: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=2)
    fuel_out: Decimal = Field(..., ge=Decimal("0.00"), le=Decimal("100.00"), decimal_places=2)


class ReturnRequest(BaseModel):
    odometer_in: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=2)
    fuel_in: Decimal = Field(..., ge=Decimal("0.00"), le=Decimal("100.00"), decimal_places=2)
    damage_notes: Optional[str] = Field(None, max_length=1000)
    fuel_charge: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"), decimal_places=2)
    damage_charge: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"), decimal_places=2)


class RentalResponse(BaseModel):
    id: int
    booking_id: int
    actual_pickup_at: datetime
    actual_drop_at: Optional[datetime] = None
    odometer_out: Decimal
    odometer_in: Optional[Decimal] = None
    fuel_out: Decimal
    fuel_in: Optional[Decimal] = None
    damage_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
