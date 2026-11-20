import time
from typing import Dict, List
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import (
    CustomerRegisterRequest,
    StaffCreateRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.core.security import require_role
from app.core.config import settings
from app.exceptions import AppException, BadRequestException

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory rate limiter per IP for login
_login_attempts: Dict[str, List[float]] = {}


def rate_limit_login(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    attempts = _login_attempts.get(client_ip, [])
    # Keep attempts within the last 60 seconds
    attempts = [t for t in attempts if now - t < 60.0]
    if len(attempts) >= settings.LOGIN_RATE_LIMIT_PER_MINUTE:
        raise AppException(
            message="Too many login attempts. Please try again after 1 minute.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )
    attempts.append(now)
    _login_attempts[client_ip] = attempts


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_customer(req: CustomerRegisterRequest, db: Session = Depends(get_db)):
    return AuthService.register_customer(db, req)


@router.post(
    "/login",
    response_model=TokenResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "format": "email", "example": "admin@rentalapp.com"},
                            "password": {"type": "string", "format": "password", "example": "Admin@123"}
                        },
                        "required": ["email", "password"]
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "example": "admin@rentalapp.com"},
                            "password": {"type": "string", "format": "password", "example": "Admin@123"}
                        },
                        "required": ["username", "password"]
                    }
                }
            }
        }
    }
)
async def login(
    request: Request,
    db: Session = Depends(get_db),
    _rate_limit: None = Depends(rate_limit_login),
):
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
    else:
        try:
            data = await request.json()
        except Exception:
            raise BadRequestException("Invalid request body")
        username = data.get("email") or data.get("username")
        password = data.get("password")

    if not username or not password:
        raise BadRequestException("Email/username and password are required")

    login_req = LoginRequest(email=str(username), password=str(password))
    return AuthService.login(db, login_req)


@router.post("/staff", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_branch_staff(
    req: StaffCreateRequest,
    db: Session = Depends(get_db),
    _admin=Depends(require_role("ADMIN")),
):
    return AuthService.create_branch_staff(db, req)
