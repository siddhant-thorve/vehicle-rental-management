import math
import uuid
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal
from typing import Optional, List

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import AUTH_SERVICE_URL, CATALOG_SERVICE_URL, FLEET_SERVICE_URL
from app.core.security import CurrentUser, get_current_user, require_role
from app.db.session import get_db
from app.models.entities import Booking
from app.repositories import booking as repositories
from app.schemas.api import (
    BookingCreate,
    BookingResponse,
    BookingStatusUpdate,
    CancelResponse,
    QuoteRequest,
    QuoteResponse,
)
from app.services.pricing import calculate_cheapest_rate
from app.services.internal import (
    get_booking_record,
    list_report_bookings,
    update_status,
)

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Health Check")
def health():
    return {"status": "ok", "service": "booking-service"}


@router.get("/availability", tags=["Availability"], summary="Conflict-Free Availability Search")
def get_availability(
    branch_id: int,
    category_id: int,
    pickup_at: datetime,
    drop_at: datetime,
    db: Session = Depends(get_db),
):
    if pickup_at.tzinfo is None:
        pickup_at = pickup_at.replace(tzinfo=timezone.utc)
    if drop_at.tzinfo is None:
        drop_at = drop_at.replace(tzinfo=timezone.utc)

    duration_hours = math.ceil((drop_at - pickup_at).total_seconds() / 3600.0)
    if duration_hours < 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Minimum rental duration is 4 hours")

    try:
        resp = httpx.get(
            f"{FLEET_SERVICE_URL}/vehicles",
            params={"branch_id": branch_id, "category_id": category_id, "status": "AVAILABLE", "size": 100},
            timeout=5.0,
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch vehicles from fleet service")
        vehicles = resp.json()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Fleet service unavailable: {str(e)}")

    available_vehicles = []
    for v in vehicles:
        if not repositories.has_booking_overlap(db, v["id"], pickup_at, drop_at):
            available_vehicles.append(v)

    return {
        "branch_id": branch_id,
        "category_id": category_id,
        "pickup_at": pickup_at,
        "drop_at": drop_at,
        "duration_hours": duration_hours,
        "available_count": len(available_vehicles),
        "vehicles": available_vehicles,
    }


@router.post("/bookings/quote", response_model=QuoteResponse, tags=["Bookings"], summary="Calculate Estimated Quote")
def get_quote(req: QuoteRequest):
    pickup_at = req.pickup_at
    drop_at = req.drop_at
    if pickup_at.tzinfo is None:
        pickup_at = pickup_at.replace(tzinfo=timezone.utc)
    if drop_at.tzinfo is None:
        drop_at = drop_at.replace(tzinfo=timezone.utc)

    duration_hours = math.ceil((drop_at - pickup_at).total_seconds() / 3600.0)
    if duration_hours < 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Minimum rental duration is 4 hours")

    try:
        resp = httpx.get(f"{CATALOG_SERVICE_URL}/tariffs/category/{req.category_id}", timeout=5.0)
        if resp.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No active tariff for category {req.category_id}")
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch tariff")
        tariff = resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Fleet service unavailable: {str(e)}")

    estimated_amount, breakdown = calculate_cheapest_rate(
        hourly_rate=Decimal(str(tariff["hourly_rate"])),
        daily_rate=Decimal(str(tariff["daily_rate"])),
        weekly_rate=Decimal(str(tariff["weekly_rate"])),
        duration_hours=duration_hours,
    )
    deposit_amount = Decimal(str(tariff["deposit_amount"]))
    total_upfront = estimated_amount + deposit_amount

    return QuoteResponse(
        category_id=req.category_id,
        duration_hours=duration_hours,
        estimated_amount=estimated_amount,
        deposit_amount=deposit_amount,
        total_upfront=total_upfront,
        breakdown=breakdown,
    )


@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED, tags=["Bookings"], summary="[CUSTOMER] Create Booking")
def create_booking(
    req: BookingCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role(["CUSTOMER"])),
):
    licence_verified = current_user.licence_verified
    if not licence_verified:
        try:
            resp = httpx.get(f"{AUTH_SERVICE_URL}/internal/users/{current_user.id}", timeout=5.0)
            if resp.status_code == 200:
                licence_verified = resp.json().get("licence_verified", False)
        except Exception:
            pass

    if not licence_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Customer driving licence is not verified. Please contact branch staff."
        )

    now = datetime.now(timezone.utc)
    pickup_at = req.pickup_at
    drop_at = req.drop_at
    if pickup_at.tzinfo is None:
        pickup_at = pickup_at.replace(tzinfo=timezone.utc)
    if drop_at.tzinfo is None:
        drop_at = drop_at.replace(tzinfo=timezone.utc)

    if pickup_at <= now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pickup time must be in the future")

    duration_hours = math.ceil((drop_at - pickup_at).total_seconds() / 3600.0)
    if duration_hours < 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Minimum rental duration is 4 hours")

    try:
        resp = httpx.get(f"{FLEET_SERVICE_URL}/vehicles/{req.vehicle_id}", timeout=5.0)
        if resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vehicle ID {req.vehicle_id} not found")
        vehicle = resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Fleet service unavailable: {str(e)}")

    if vehicle["status"] in ["UNDER_MAINTENANCE", "RETIRED"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Vehicle is {vehicle['status']} and cannot be booked")

    if repositories.has_booking_overlap(db, req.vehicle_id, pickup_at, drop_at):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vehicle is already booked for this time window")

    try:
        resp = httpx.get(f"{CATALOG_SERVICE_URL}/tariffs/category/{req.category_id}", timeout=5.0)
        if resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tariff not found")
        tariff = resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Fleet service unavailable: {str(e)}")

    estimated_amount, _ = calculate_cheapest_rate(
        hourly_rate=Decimal(str(tariff["hourly_rate"])),
        daily_rate=Decimal(str(tariff["daily_rate"])),
        weekly_rate=Decimal(str(tariff["weekly_rate"])),
        duration_hours=duration_hours,
    )
    deposit_amount = Decimal(str(tariff["deposit_amount"]))

    booking_no = f"BK-{uuid.uuid4().hex[:8].upper()}"
    booking = Booking(
        booking_no=booking_no,
        customer_id=current_user.id,
        vehicle_id=req.vehicle_id,
        branch_id=req.branch_id,
        pickup_at=pickup_at,
        drop_at=drop_at,
        estimated_amount=estimated_amount,
        deposit_amount=deposit_amount,
        refund_amount=Decimal("0.00"),
        status="CONFIRMED",
    )
    return repositories.create_booking(db, booking)


@router.get("/bookings/me", response_model=List[BookingResponse], tags=["Bookings"], summary="[CUSTOMER] View My Bookings")
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role(["CUSTOMER"])),
):
    return repositories.list_customer_bookings(db, current_user.id)


@router.get("/bookings/{booking_id:int}", response_model=BookingResponse, tags=["Bookings"], summary="[CUSTOMER / STAFF / ADMIN] View Single Booking Details")
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    booking = repositories.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if current_user.role == "CUSTOMER" and current_user.id != booking.customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access other customer's booking")
    if current_user.role == "BRANCH_STAFF" and current_user.branch_id != booking.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access another branch's booking")

    return booking


@router.patch("/bookings/{booking_id}/cancel", response_model=CancelResponse, tags=["Bookings"], summary="[CUSTOMER] Cancel Booking with Refund Policy")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role(["CUSTOMER"])),
):
    booking = repositories.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot cancel another customer's booking")

    if booking.status != "CONFIRMED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel booking with status {booking.status}")

    now = datetime.now(timezone.utc)
    pickup_at = booking.pickup_at
    if pickup_at.tzinfo is None:
        pickup_at = pickup_at.replace(tzinfo=timezone.utc)

    hours_until_pickup = (pickup_at - now).total_seconds() / 3600.0

    if hours_until_pickup > 24:
        refund_amount = booking.deposit_amount
        msg = "Full refund granted (cancelled more than 24 hours before pickup)"
    elif hours_until_pickup > 0:
        refund_amount = (booking.deposit_amount * Decimal("0.50")).quantize(Decimal("0.01"))
        msg = "50% refund granted (cancelled within 24 hours of pickup)"
    else:
        refund_amount = Decimal("0.00")
        msg = "No refund (cancelled after scheduled pickup time)"

    repositories.cancel_booking(db, booking, refund_amount)

    return CancelResponse(
        booking_id=booking.id,
        status="CANCELLED",
        refund_amount=refund_amount,
        message=msg,
    )


@router.get("/bookings/branch", response_model=List[BookingResponse], tags=["Bookings"], summary="[BRANCH_STAFF] View Branch Bookings by Date")
def get_branch_bookings(
    date_filter: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db),
    staff: CurrentUser = Depends(require_role(["BRANCH_STAFF", "ADMIN"])),
):
    branch_id = staff.branch_id if staff.role == "BRANCH_STAFF" else None
    start_dt = None
    end_dt = None
    if date_filter:
        start_dt = datetime.combine(date_filter, datetime.min.time(), tzinfo=timezone.utc)
        end_dt = datetime.combine(date_filter, datetime.max.time(), tzinfo=timezone.utc)
    return repositories.list_branch_bookings(db, branch_id, start_dt, end_dt)


@router.get(
    "/internal/bookings/{booking_id}",
    response_model=BookingResponse,
    include_in_schema=False,
)
def get_booking_internal(booking_id: int, db: Session = Depends(get_db)):
    booking = get_booking_record(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking


@router.patch(
    "/internal/bookings/{booking_id}/status",
    response_model=BookingResponse,
    include_in_schema=False,
)
def update_booking_status_internal(
    booking_id: int,
    req: BookingStatusUpdate,
    db: Session = Depends(get_db),
):
    booking = get_booking_record(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    try:
        return update_status(db, booking, req.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get(
    "/internal/reports/bookings",
    response_model=List[BookingResponse],
    include_in_schema=False,
)
def list_report_bookings_internal(
    branch_id: int,
    start_at: datetime,
    end_at: datetime,
    db: Session = Depends(get_db),
):
    return list_report_bookings(db, branch_id, start_at, end_at)
