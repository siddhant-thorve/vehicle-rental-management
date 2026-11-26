from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class QuoteRequest(BaseModel):
    category_id: int
    pickup_at: datetime
    drop_at: datetime


class QuoteResponse(BaseModel):
    category_id: int
    duration_hours: int
    estimated_amount: Decimal
    deposit_amount: Decimal
    total_upfront: Decimal
    breakdown: dict[str, Any]


class BookingCreate(BaseModel):
    vehicle_id: int
    branch_id: int
    category_id: int
    pickup_at: datetime
    drop_at: datetime


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

    class Config:
        from_attributes = True


class CancelResponse(BaseModel):
    booking_id: int
    status: str
    refund_amount: Decimal
    message: str


class BookingStatusUpdate(BaseModel):
    status: str
