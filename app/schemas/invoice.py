from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


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
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
