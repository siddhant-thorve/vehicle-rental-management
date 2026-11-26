import math
from datetime import datetime, timezone
from decimal import Decimal

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import CATALOG_SERVICE_URL, FLEET_SERVICE_URL
from app.exceptions import BookingNotFound, BookingServiceUnavailable
from app.models.entities import Invoice, Rental
from app.repositories import operations as repositories
from app.schemas.api import ReturnRequest
from app.services import booking_client


def fetch_booking(booking_id: int):
    try:
        return booking_client.get_booking(booking_id)
    except BookingNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except BookingServiceUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc


def set_booking_status(booking_id: int, new_status: str) -> None:
    try:
        booking_client.update_booking_status(booking_id, new_status)
    except BookingServiceUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc


def update_fleet_vehicle(
    vehicle_id: int, vehicle_status: str, odometer_km: float
) -> None:
    try:
        response = httpx.patch(
            f"{FLEET_SERVICE_URL}/internal/vehicles/{vehicle_id}/status",
            json={"status": vehicle_status, "odometer_km": odometer_km},
            timeout=5.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Fleet service update failed: {exc}",
        ) from exc


def get_fleet_vehicle(vehicle_id: int) -> dict:
    try:
        response = httpx.get(
            f"{FLEET_SERVICE_URL}/vehicles/{vehicle_id}", timeout=5.0
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Fleet service communication failed: {exc}",
        ) from exc
    return response.json()


def get_tariff(category_id: int) -> dict:
    try:
        response = httpx.get(
            f"{CATALOG_SERVICE_URL}/tariffs/category/{category_id}", timeout=5.0
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch tariff: {exc}",
        ) from exc
    return response.json()


def record_pickup(
    db: Session, booking, odometer_out: Decimal, fuel_out: Decimal
) -> Rental:
    update_fleet_vehicle(
        booking.vehicle_id, "BOOKED", float(odometer_out)
    )
    set_booking_status(booking.id, "IN_PROGRESS")
    rental = Rental(
        booking_id=booking.id,
        actual_pickup_at=datetime.now(timezone.utc),
        actual_drop_at=None,
        odometer_out=odometer_out,
        odometer_in=None,
        fuel_out=fuel_out,
        fuel_in=None,
        damage_notes=None,
    )
    return repositories.create_rental(db, rental)


def calculate_invoice(
    booking,
    rental: Rental,
    request: ReturnRequest,
    tariff: dict,
    returned_at: datetime,
) -> Invoice:
    base_amount = booking.estimated_amount
    total_km_driven = request.odometer_in - rental.odometer_out
    actual_pickup = rental.actual_pickup_at
    if actual_pickup.tzinfo is None:
        actual_pickup = actual_pickup.replace(tzinfo=timezone.utc)

    rental_days = max(
        1, math.ceil(max((returned_at - actual_pickup).total_seconds(), 0) / 86400.0)
    )
    free_km_total = Decimal(str(tariff["free_km_per_day"])) * rental_days
    extra_km_amount = (
        (total_km_driven - free_km_total)
        * Decimal(str(tariff["extra_km_rate"]))
    ).quantize(Decimal("0.01")) if total_km_driven > free_km_total else Decimal("0.00")

    scheduled_drop = booking.drop_at
    if scheduled_drop.tzinfo is None:
        scheduled_drop = scheduled_drop.replace(tzinfo=timezone.utc)
    late_hours = (
        math.ceil((returned_at - scheduled_drop).total_seconds() / 3600.0)
        if returned_at > scheduled_drop
        else 0
    )
    extra_hour_amount = (
        Decimal(late_hours) * Decimal(str(tariff["extra_hour_rate"]))
    ).quantize(Decimal("0.01"))

    fuel_charge = request.fuel_charge.quantize(Decimal("0.01"))
    damage_charge = request.damage_charge.quantize(Decimal("0.01"))
    subtotal = base_amount + extra_km_amount + extra_hour_amount + fuel_charge + damage_charge
    tax_amount = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
    total_amount = subtotal + tax_amount
    deposit_adjusted = min(booking.deposit_amount, total_amount).quantize(Decimal("0.01"))
    payable_amount = max(Decimal("0.00"), total_amount - deposit_adjusted).quantize(Decimal("0.01"))

    return Invoice(
        rental_id=rental.id,
        base_amount=base_amount,
        extra_km_amount=extra_km_amount,
        extra_hour_amount=extra_hour_amount,
        fuel_charge=fuel_charge,
        damage_charge=damage_charge,
        tax_amount=tax_amount,
        total_amount=total_amount,
        deposit_adjusted=deposit_adjusted,
        payable_amount=payable_amount,
        generated_at=returned_at,
    )


def record_return(
    db: Session,
    booking,
    rental: Rental,
    request: ReturnRequest,
) -> Invoice:
    vehicle = get_fleet_vehicle(booking.vehicle_id)
    tariff = get_tariff(vehicle["category_id"])
    now = datetime.now(timezone.utc)
    invoice = calculate_invoice(booking, rental, request, tariff, now)

    update_fleet_vehicle(
        booking.vehicle_id, "AVAILABLE", float(request.odometer_in)
    )
    set_booking_status(booking.id, "COMPLETED")
    return repositories.complete_rental(
        db,
        rental,
        invoice,
        now,
        request.odometer_in,
        request.fuel_in,
        request.damage_notes,
    )


def list_report_bookings(branch_id: int, start_at: datetime, end_at: datetime):
    try:
        return booking_client.list_report_bookings(
            branch_id, start_at.isoformat(), end_at.isoformat()
        )
    except BookingServiceUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
