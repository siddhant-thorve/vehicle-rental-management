from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.booking import (
    QuoteRequest,
    QuoteResponse,
    BookingCreate,
    BookingResponse,
    CancelResponse,
)
from app.schemas.common import PaginatedResponse
from app.services.booking_service import BookingService
from app.core.security import require_role, get_current_user
from app.models.user import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/quote", response_model=QuoteResponse)
def get_booking_quote(
    req: QuoteRequest,
    db: Session = Depends(get_db),
    _customer=Depends(require_role("CUSTOMER")),
):
    return BookingService.get_quote(db, req)


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    req: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CUSTOMER")),
):
    return BookingService.create_booking(db, req, current_user)


@router.get("/me", response_model=PaginatedResponse[BookingResponse])
def get_my_bookings(
    status: Optional[str] = Query(None, description="Filter by booking status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CUSTOMER")),
):
    items, total = BookingService.list_my_bookings(
        db=db,
        current_user=current_user,
        status=status,
        page=page,
        size=size,
    )
    return PaginatedResponse(items=items, total=total, page=page, size=size)


@router.get("/branch", response_model=PaginatedResponse[BookingResponse])
def get_branch_bookings(
    target_date: date = Query(..., alias="date", description="Target date to view branch bookings (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("BRANCH_STAFF")),
):
    items, total = BookingService.list_branch_bookings(
        db=db,
        current_user=current_user,
        target_date=target_date,
        page=page,
        size=size,
    )
    return PaginatedResponse(items=items, total=total, page=page, size=size)


@router.get("/{id}", response_model=BookingResponse)
def get_booking_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BookingService.get_booking_by_id(db, id, current_user)


@router.patch("/{id}/cancel", response_model=CancelResponse)
def cancel_booking(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CUSTOMER")),
):
    return BookingService.cancel_booking(db, id, current_user)
