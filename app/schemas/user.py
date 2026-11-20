from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CustomerCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15, pattern=r"^\+?[0-9]{10,15}$")
    licence_no: str = Field(..., min_length=5, max_length=50)


class CustomerResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str
    licence_no: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
