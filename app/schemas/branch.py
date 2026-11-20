from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class BranchBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    city: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=5, max_length=300)
    contact_no: str = Field(..., min_length=8, max_length=20)


class BranchCreate(BranchBase):
    pass


class BranchResponse(BranchBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
