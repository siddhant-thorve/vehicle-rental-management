from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class BookingStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class QuoteRequest(BaseModel):
    category_id: int = Field(..., gt=0)
    pickup_at: datetime
    drop_at: datetime


class QuoteResponse(BaseModel):
    category_id: int
    duration_hours: int
    estimated_amount: Decimal
    deposit_amount: Decimal
    total_upfront: Decimal
    breakdown: Dict[str, Any]


class BookingCreate(BaseModel):
    vehicle_id: int = Field(..., gt=0)
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
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CancelResponse(BaseModel):
    booking_id: int
    booking_no: str
    status: BookingStatus
    refund_amount: Decimal
    message: str
