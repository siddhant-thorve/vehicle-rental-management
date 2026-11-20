from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.core.security import mask_licence_number


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    BRANCH_STAFF = "BRANCH_STAFF"
    CUSTOMER = "CUSTOMER"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15, pattern=r"^\+?[0-9]{10,15}$")


class CustomerRegisterRequest(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    licence_no: str = Field(..., min_length=5, max_length=50)


class StaffCreateRequest(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    branch_id: int = Field(..., gt=0)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str
    licence_no: Optional[str] = None
    licence_verified: bool
    role: str
    branch_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(UserResponse):
    @field_validator("licence_no", mode="after")
    @classmethod
    def mask_licence(cls, v: Optional[str]) -> Optional[str]:
        return mask_licence_number(v)
