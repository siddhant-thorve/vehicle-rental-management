from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_serializer


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=8, max_length=20)
    licence_no: Optional[str] = None


class StaffCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=8, max_length=20)
    branch_id: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str
    licence_no: Optional[str] = None
    licence_verified: bool
    role: str
    branch_id: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True

    @field_serializer("licence_no")
    def mask_licence_no(self, licence_no: Optional[str]) -> Optional[str]:
        if licence_no is None:
            return None
        if len(licence_no) <= 6:
            return "*" * len(licence_no)
        return f"{licence_no[:2]}****{licence_no[-4:]}"
