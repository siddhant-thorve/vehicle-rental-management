import math
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
import logging

from app.models.rental import Rental
from app.models.invoice import Invoice
from app.models.user import User
from app.schemas.rental import PickupRequest, ReturnRequest
from app.schemas.booking import BookingStatus
from app.schemas.vehicle import VehicleStatus
from app.repositories.rental_repo import RentalRepository
from app.repositories.booking_repo import BookingRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.repositories.tariff_repo import TariffRepository
from app.repositories.invoice_repo import InvoiceRepository
from app.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException,
)

logger = logging.getLogger("rental_audit")


class RentalService:
    @staticmethod
    def record_pickup(
        db: Session,
        booking_id: int,
        req: PickupRequest,
        current_user: User,
    ) -> Rental:
        booking = BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise NotFoundException(f"Booking ID {booking_id} not found")

        # Security check: Branch staff can only act on bookings for their own branch
        if current_user.role == "BRANCH_STAFF" and current_user.branch_id != booking.branch_id:
            raise ForbiddenException("Branch staff cannot act on a booking belonging to another branch")

        # Business Rule 6: Pickup is allowed only for CONFIRMED bookings
        if booking.status != BookingStatus.CONFIRMED.value:
            raise BadRequestException(f"Pickup is only permitted for CONFIRMED bookings (current status: {booking.status})")

        existing_rental = RentalRepository.get_by_booking_id(db, booking_id)
        if existing_rental:
            raise ConflictException("Rental has already been started for this booking")

        vehicle = VehicleRepository.get_vehicle_by_id(db, booking.vehicle_id)
        if not vehicle:
            raise NotFoundException(f"Vehicle ID {booking.vehicle_id} not found")

        now = datetime.now(timezone.utc)

        rental = Rental(
            booking_id=booking.id,
            actual_pickup_at=now,
            actual_drop_at=None,
            odometer_out=req.odometer_out,
            odometer_in=None,
            fuel_out=req.fuel_out,
            fuel_in=None,
            damage_notes=None,
        )
        created_rental = RentalRepository.create(db, rental)

        # Update booking status to IN_PROGRESS
        booking.status = BookingStatus.IN_PROGRESS.value
        BookingRepository.update(db, booking)

        # Business Rule 9: Vehicle status is set to BOOKED on pickup
        vehicle.status = VehicleStatus.BOOKED.value
        vehicle.odometer_km = req.odometer_out
        VehicleRepository.update_vehicle(db, vehicle)

        logger.info(f"AUDIT: Vehicle pickup recorded for Booking {booking.booking_no} by User {current_user.id}")
        return created_rental

    @staticmethod
    def record_return(
        db: Session,
        booking_id: int,
        req: ReturnRequest,
        current_user: User,
    ) -> Invoice:
        booking = BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise NotFoundException(f"Booking ID {booking_id} not found")

        # Security check: Branch staff can only act on their own branch's booking
        if current_user.role == "BRANCH_STAFF" and current_user.branch_id != booking.branch_id:
            raise ForbiddenException("Branch staff cannot act on a booking belonging to another branch")

        # Business Rule 6: return only for IN_PROGRESS rentals
        if booking.status != BookingStatus.IN_PROGRESS.value:
            raise BadRequestException(f"Return is only permitted for IN_PROGRESS rentals (current status: {booking.status})")

        rental = RentalRepository.get_by_booking_id(db, booking_id)
        if not rental:
            raise NotFoundException(f"Rental record not found for Booking ID {booking_id}")

        if rental.actual_drop_at is not None:
            raise ConflictException("Vehicle return has already been processed for this rental")

        # Business Rule 7: odometer_in must be greater than or equal to odometer_out
        if req.odometer_in < rental.odometer_out:
            raise BadRequestException(
                f"odometer_in ({req.odometer_in}) must be greater than or equal to odometer_out ({rental.odometer_out})"
            )

        now = datetime.now(timezone.utc)
        rental.actual_drop_at = now
        rental.odometer_in = req.odometer_in
        rental.fuel_in = req.fuel_in
        rental.damage_notes = req.damage_notes
        RentalRepository.update(db, rental)

        # Vehicle updates: status back to AVAILABLE, odometer updated
        vehicle = VehicleRepository.get_vehicle_by_id(db, booking.vehicle_id)
        if vehicle:
            # Business Rule 9: Vehicle status is set back to AVAILABLE on return
            vehicle.status = VehicleStatus.AVAILABLE.value
            vehicle.odometer_km = req.odometer_in
            VehicleRepository.update_vehicle(db, vehicle)

        # Booking update: COMPLETED
        booking.status = BookingStatus.COMPLETED.value
        BookingRepository.update(db, booking)

        # --- Settlement & Invoice Computation ---
        tariff = TariffRepository.get_active_by_category(db, vehicle.category_id)
        if not tariff:
            raise NotFoundException(f"Tariff not found for category {vehicle.category_id}")

        base_amount = booking.estimated_amount

        # Extra-km computation
        total_km_driven = req.odometer_in - rental.odometer_out
        actual_pickup = rental.actual_pickup_at
        if actual_pickup.tzinfo is None:
            actual_pickup = actual_pickup.replace(tzinfo=timezone.utc)

        duration_seconds = max((now - actual_pickup).total_seconds(), 0)
        rental_days = max(1, math.ceil(duration_seconds / 86400.0))
        free_km_total = tariff.free_km_per_day * Decimal(rental_days)

        if total_km_driven > free_km_total:
            extra_km = total_km_driven - free_km_total
            extra_km_amount = (extra_km * tariff.extra_km_rate).quantize(Decimal("0.01"))
        else:
            extra_km_amount = Decimal("0.00")

        # Extra-hour computation (late return)
        scheduled_drop = booking.drop_at
        if scheduled_drop.tzinfo is None:
            scheduled_drop = scheduled_drop.replace(tzinfo=timezone.utc)

        if now > scheduled_drop:
            late_seconds = (now - scheduled_drop).total_seconds()
            late_hours = math.ceil(late_seconds / 3600.0)
            extra_hour_amount = (Decimal(late_hours) * tariff.extra_hour_rate).quantize(Decimal("0.01"))
        else:
            extra_hour_amount = Decimal("0.00")

        fuel_charge = req.fuel_charge.quantize(Decimal("0.01"))
        damage_charge = req.damage_charge.quantize(Decimal("0.01"))

        subtotal = base_amount + extra_km_amount + extra_hour_amount + fuel_charge + damage_charge
        tax_amount = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))  # 18% standard GST
        total_amount = subtotal + tax_amount

        deposit_adjusted = min(booking.deposit_amount, total_amount).quantize(Decimal("0.01"))
        payable_amount = max(Decimal("0.00"), total_amount - deposit_adjusted).quantize(Decimal("0.01"))

        invoice = Invoice(
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
            generated_at=now,
        )
        created_invoice = InvoiceRepository.create(db, invoice)
        logger.info(
            f"AUDIT: Invoice ID {created_invoice.id} generated for Rental ID {rental.id}. "
            f"Total: {total_amount}, Payable: {payable_amount}"
        )
        return created_invoice

    @staticmethod
    def get_invoice_by_rental_id(db: Session, rental_id: int, current_user: User) -> Invoice:
        invoice = InvoiceRepository.get_by_rental_id(db, rental_id)
        if not invoice:
            raise NotFoundException(f"Invoice for Rental ID {rental_id} not found")

        rental = RentalRepository.get_by_id(db, rental_id)
        if not rental:
            raise NotFoundException(f"Rental ID {rental_id} not found")

        booking = BookingRepository.get_by_id(db, rental.booking_id)
        if not booking:
            raise NotFoundException(f"Booking for Rental ID {rental_id} not found")

        # Security check: Customer can only view their own invoice
        if current_user.role == "CUSTOMER" and booking.customer_id != current_user.id:
            raise ForbiddenException("Access denied: You can only view invoices for your own bookings")

        # Security check: Branch staff can only view invoices belonging to their branch
        if current_user.role == "BRANCH_STAFF" and current_user.branch_id != booking.branch_id:
            raise ForbiddenException("Access denied: Invoice belongs to another branch")

        return invoice
