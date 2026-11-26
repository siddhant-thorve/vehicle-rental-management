import math
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import FLEET_SERVICE_URL
from app.core.security import CurrentUser, get_current_user, require_role
from app.db.session import get_db
from app.models.entities import Invoice, Rental
from app.repositories import operations as repositories
from app.schemas.api import InvoiceResponse, PickupRequest, RentalResponse, ReturnRequest
from app.services.operations import (
    fetch_booking,
    list_report_bookings,
    record_pickup,
    record_return,
)

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Health Check")
def health():
    return {"status": "ok", "service": "rental-operations-service"}


@router.post(
    "/rentals/{booking_id}/pickup",
    response_model=RentalResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Rental Lifecycle"],
    summary="[BRANCH_STAFF] Record Vehicle Pickup",
)
def pickup(
    booking_id: int,
    req: PickupRequest,
    db: Session = Depends(get_db),
    staff: CurrentUser = Depends(require_role(["BRANCH_STAFF", "ADMIN"])),
):
    booking = fetch_booking(booking_id)
    if staff.role == "BRANCH_STAFF" and staff.branch_id != booking.branch_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot act on booking belonging to another branch",
        )
    if booking.status != "CONFIRMED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pickup only allowed for CONFIRMED bookings (current: {booking.status})",
        )
    if repositories.get_rental_for_booking(db, booking_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Rental already recorded for this booking",
        )
    return record_pickup(db, booking, req.odometer_out, req.fuel_out)


@router.post(
    "/rentals/{booking_id}/return",
    response_model=InvoiceResponse,
    tags=["Rental Lifecycle"],
    summary="[BRANCH_STAFF] Record Return & Generate Invoice",
)
def return_vehicle(
    booking_id: int,
    req: ReturnRequest,
    db: Session = Depends(get_db),
    staff: CurrentUser = Depends(require_role(["BRANCH_STAFF", "ADMIN"])),
):
    booking = fetch_booking(booking_id)
    if staff.role == "BRANCH_STAFF" and staff.branch_id != booking.branch_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot act on booking belonging to another branch",
        )
    if booking.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Return only allowed for IN_PROGRESS rentals (current: {booking.status})",
        )
    rental = repositories.get_rental_for_booking(db, booking_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental record not found",
        )
    if rental.actual_drop_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Return already recorded",
        )
    if req.odometer_in < rental.odometer_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"odometer_in ({req.odometer_in}) must be greater than or equal to "
                f"odometer_out ({rental.odometer_out})"
            ),
        )
    return record_return(db, booking, rental, req)


@router.get(
    "/invoices/{rental_id}",
    response_model=InvoiceResponse,
    tags=["Invoices"],
    summary="[CUSTOMER / STAFF / ADMIN] View Settlement Invoice",
)
def get_invoice(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    invoice = repositories.get_invoice(db, rental_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )
    rental = repositories.get_rental(db, rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rental record not found"
        )
    booking = fetch_booking(rental.booking_id)
    if current_user.role == "CUSTOMER" and current_user.id != booking.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another customer's invoice",
        )
    if (
        current_user.role == "BRANCH_STAFF"
        and current_user.branch_id != booking.branch_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another branch's invoice",
        )
    return invoice


@router.get(
    "/reports/utilisation",
    tags=["Reporting & Analytics"],
    summary="[ADMIN] Fleet Utilisation Report",
)
def get_utilisation_report(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    admin: CurrentUser = Depends(require_role(["ADMIN"])),
):
    from_date = from_date or date.today() - timedelta(days=30)
    to_date = to_date or date.today()
    start_dt = datetime.combine(from_date, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(to_date, time.max, tzinfo=timezone.utc)
    days = max(1, (to_date - from_date).days + 1)

    try:
        response = httpx.get(f"{FLEET_SERVICE_URL}/branches?size=100", timeout=5.0)
        response.raise_for_status()
        branches = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Fleet service error: {exc}",
        ) from exc

    reports = []
    for branch in branches:
        try:
            response = httpx.get(
                f"{FLEET_SERVICE_URL}/vehicles",
                params={"branch_id": branch["id"], "size": 100},
                timeout=5.0,
            )
            response.raise_for_status()
            vehicles = response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Fleet service error: {exc}",
            ) from exc

        bookings = list_report_bookings(
            branch["id"], start_dt, end_dt
        )
        booked_hours = sum(
            math.ceil(
                (
                    datetime.fromisoformat(booking["drop_at"])
                    - datetime.fromisoformat(booking["pickup_at"])
                ).total_seconds()
                / 3600.0
            )
            for booking in bookings
        )
        active_vehicles = sum(
            1 for vehicle in vehicles if vehicle.get("status") != "RETIRED"
        )
        available_hours = active_vehicles * days * 24
        reports.append(
            {
                "branch_id": branch["id"],
                "branch_name": branch["name"],
                "city": branch["city"],
                "total_vehicles": len(vehicles),
                "active_vehicles": active_vehicles,
                "total_rentals": len(bookings),
                "total_booked_hours": booked_hours,
                "total_fleet_available_hours": available_hours,
                "utilisation_percentage": (
                    round((booked_hours / available_hours) * 100, 2)
                    if available_hours
                    else 0.0
                ),
            }
        )

    return {
        "from_date": from_date,
        "to_date": to_date,
        "days_in_period": days,
        "branches": reports,
    }


@router.get(
    "/reports/revenue",
    tags=["Reporting & Analytics"],
    summary="[ADMIN] Revenue Report",
)
def get_revenue_report(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_role(["ADMIN"])),
):
    from_date = from_date or date.today() - timedelta(days=30)
    to_date = to_date or date.today()
    start_dt = datetime.combine(from_date, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(to_date, time.max, tzinfo=timezone.utc)
    invoices = repositories.list_invoices(db, start_dt, end_dt)
    return {
        "from_date": from_date,
        "to_date": to_date,
        "invoice_count": len(invoices),
        "total_revenue": sum(invoice.total_amount for invoice in invoices),
        "total_deposit_adjusted": sum(
            invoice.deposit_adjusted for invoice in invoices
        ),
        "total_payable_amount": sum(
            invoice.payable_amount for invoice in invoices
        ),
    }
