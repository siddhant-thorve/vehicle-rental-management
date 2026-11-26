from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class PickupRequest(BaseModel):
    odometer_out: Decimal = Field(..., ge=0)
    fuel_out: Decimal = Field(..., ge=0, le=100)


class ReturnRequest(BaseModel):
    odometer_in: Decimal = Field(..., ge=0)
    fuel_in: Decimal = Field(..., ge=0, le=100)
    fuel_charge: Decimal = Field(default=Decimal("0.00"), ge=0)
    damage_charge: Decimal = Field(default=Decimal("0.00"), ge=0)
    damage_notes: Optional[str] = None


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

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    rental_id: int
    base_amount: Decimal
    extra_km_amount: Decimal
    extra_hour_amount: Decimal
    fuel_charge: Decimal
    damage_charge: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    deposit_adjusted: Decimal
    payable_amount: Decimal
    generated_at: datetime

    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    id: int
    booking_no: str
    customer_id: int
    vehicle_id: int
    branch_id: int
    pickup_at: datetime
    drop_at: datetime
    estimated_amount: Decimal
    deposit_amount: Decimal
    refund_amount: Decimal
    status: str
    created_at: datetime
