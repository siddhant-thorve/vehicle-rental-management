from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_role,
    verify_password,
)
from app.db.session import get_db
from app.models.entities import User
from app.repositories.users import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_customer_licence,
)
from app.schemas.api import (
    RegisterRequest,
    StaffCreateRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Health Check")
def health():
    return {"status": "ok", "service": "auth-service"}


# 1. Customer Registration
@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"], summary="Register New Customer")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    new_user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        phone=req.phone,
        licence_no=req.licence_no,
        licence_verified=False,
        role="CUSTOMER",
        branch_id=None,
        is_active=True,
    )
    return create_user(db, new_user)


# 2. Login (Supports JSON body & Swagger UI Form Data)
@router.post("/auth/login", response_model=TokenResponse, tags=["Authentication"], summary="Authenticate and Obtain Access Token")
async def login(
    request: Request,
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        login_email = username or email
    else:
        try:
            body = await request.json()
            login_email = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")

    if not login_email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email/username and password required")

    user = get_user_by_email(db, login_email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "branch_id": user.branch_id,
        "licence_verified": user.licence_verified,
    }
    token = create_access_token(token_data)
    return TokenResponse(access_token=token)


# 3. Create Branch Staff (ADMIN only)
@router.post("/auth/staff", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"], summary="[ADMIN] Create Branch Staff")
def create_staff(
    req: StaffCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN"])),
):
    existing = get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    staff = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        phone=req.phone,
        licence_no=None,
        licence_verified=True,
        role="BRANCH_STAFF",
        branch_id=req.branch_id,
        is_active=True,
    )
    return create_user(db, staff)


# 4. Verify Customer Licence (BRANCH_STAFF only)
@router.patch("/customers/{customer_id}/verify-licence", response_model=UserResponse, tags=["Customers"], summary="[BRANCH_STAFF] Verify Customer Licence")
def verify_licence(
    customer_id: int,
    db: Session = Depends(get_db),
    staff: User = Depends(require_role(["BRANCH_STAFF", "ADMIN"])),
):
    customer = get_user_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    if customer.role != "CUSTOMER":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target user is not a customer")

    return verify_customer_licence(db, customer)


# 5. Get Customer Profile
@router.get("/customers/{customer_id}", response_model=UserResponse, tags=["Customers"], summary="[CUSTOMER / STAFF / ADMIN] Get Customer Profile")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "CUSTOMER" and current_user.id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access other customer's profile")

    user = get_user_by_id(db, customer_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return user


# 6. Internal endpoint for other microservices
@router.get("/internal/users/{user_id}", response_model=UserResponse, include_in_schema=False)
def get_user_internal(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
