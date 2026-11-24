import math
import uuid
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
import logging

from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import QuoteRequest, QuoteResponse, BookingCreate, BookingStatus, CancelResponse
from app.repositories.booking_repo import BookingRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.repositories.tariff_repo import TariffRepository
from app.repositories.user_repo import UserRepository
from app.services.pricing_service import PricingService
from app.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
)

logger = logging.getLogger("booking_audit")


class BookingService:
    @staticmethod
    def get_quote(db: Session, req: QuoteRequest) -> QuoteResponse:
        pickup_at = req.pickup_at
        drop_at = req.drop_at
        if pickup_at.tzinfo is None:
            pickup_at = pickup_at.replace(tzinfo=timezone.utc)
        if drop_at.tzinfo is None:
            drop_at = drop_at.replace(tzinfo=timezone.utc)

        duration_seconds = (drop_at - pickup_at).total_seconds()
        duration_hours = math.ceil(duration_seconds / 3600.0)
        if duration_hours < 4:
            raise BadRequestException("Minimum rental duration is 4 hours")

        tariff = TariffRepository.get_active_by_category(db, req.category_id)
        if not tariff:
            raise NotFoundException(f"No active tariff defined for Category ID {req.category_id}")

        estimated_amount, breakdown = PricingService.calculate_cheapest_rate(
            hourly_rate=tariff.hourly_rate,
            daily_rate=tariff.daily_rate,
            weekly_rate=tariff.weekly_rate,
            duration_hours=duration_hours,
        )

        deposit_amount = tariff.deposit_amount
        total_upfront = estimated_amount + deposit_amount

        return QuoteResponse(
            category_id=req.category_id,
            duration_hours=duration_hours,
            estimated_amount=estimated_amount,
            deposit_amount=deposit_amount,
            total_upfront=total_upfront,
            breakdown=breakdown,
        )

    @staticmethod
    def create_booking(db: Session, req: BookingCreate, current_user: User) -> Booking:
        # Business Rule 4: Only customers with licence_verified = true may create a booking
        if not current_user.licence_verified:
            raise BadRequestException("Customer driving licence is not verified. Please contact branch staff.")

        now = datetime.now(timezone.utc)
        pickup_at = req.pickup_at
        drop_at = req.drop_at
        if pickup_at.tzinfo is None:
            pickup_at = pickup_at.replace(tzinfo=timezone.utc)
        if drop_at.tzinfo is None:
            drop_at = drop_at.replace(tzinfo=timezone.utc)

        # Business Rule 2: Minimum rental duration is 4 hours; pickup must be in the future at booking time
        if pickup_at <= now:
            raise BadRequestException("Pickup time must be in the future")

        duration_seconds = (drop_at - pickup_at).total_seconds()
        duration_hours = math.ceil(duration_seconds / 3600.0)
        if duration_hours < 4:
            raise BadRequestException("Minimum rental duration is 4 hours")

        # Check vehicle exists
        vehicle = VehicleRepository.get_vehicle_by_id(db, req.vehicle_id)
        if not vehicle or not vehicle.is_active:
            raise NotFoundException(f"Vehicle ID {req.vehicle_id} not found or inactive")

        if vehicle.status in ["UNDER_MAINTENANCE", "RETIRED"]:
            raise BadRequestException(f"Vehicle is currently {vehicle.status} and cannot be booked")

        # Business Rule 1: Overlap test: new_pickup < existing_drop AND new_drop > existing_pickup
        has_conflict = BookingRepository.has_overlap(
            db=db,
            vehicle_id=vehicle.id,
            pickup_at=pickup_at,
            drop_at=drop_at,
        )
        if has_conflict:
            raise ConflictException("Vehicle is already booked for the requested date-time window")

        # Pricing computation
        tariff = TariffRepository.get_active_by_category(db, vehicle.category_id)
        if not tariff:
            raise NotFoundException(f"No active tariff defined for Vehicle Category {vehicle.category_id}")

        estimated_amount, _ = PricingService.calculate_cheapest_rate(
            hourly_rate=tariff.hourly_rate,
            daily_rate=tariff.daily_rate,
            weekly_rate=tariff.weekly_rate,
            duration_hours=duration_hours,
        )

        # Generate unique booking number
        date_str = now.strftime("%Y%m%d")
        unique_suffix = uuid.uuid4().hex[:6].upper()
        booking_no = f"BK-{date_str}-{unique_suffix}"

        booking = Booking(
            booking_no=booking_no,
            customer_id=current_user.id,
            vehicle_id=vehicle.id,
            branch_id=vehicle.branch_id,
            pickup_at=pickup_at,
            drop_at=drop_at,
            estimated_amount=estimated_amount,
            deposit_amount=tariff.deposit_amount,
            refund_amount=Decimal("0.00"),
            status=BookingStatus.CONFIRMED.value,
        )
        created = BookingRepository.create(db, booking)
        logger.info(f"AUDIT: Booking created {created.booking_no} (ID: {created.id}) by User {current_user.id}")
        return created

    @staticmethod
    def get_booking_by_id(db: Session, booking_id: int, current_user: User) -> Booking:
        booking = BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise NotFoundException(f"Booking ID {booking_id} not found")

        # Ownership checks
        if current_user.role == "CUSTOMER" and booking.customer_id != current_user.id:
            raise ForbiddenException("Access denied: You can only view your own bookings")
        if current_user.role == "BRANCH_STAFF" and booking.branch_id != current_user.branch_id:
            raise ForbiddenException("Access denied: Booking belongs to a different branch")

        return booking

    @staticmethod
    def list_my_bookings(
        db: Session,
        current_user: User,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Booking], int]:
        skip = (page - 1) * size
        return BookingRepository.list_by_customer(
            db=db,
            customer_id=current_user.id,
            status=status,
            skip=skip,
            limit=size,
        )

    @staticmethod
    def list_branch_bookings(
        db: Session,
        current_user: User,
        target_date: date,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Booking], int]:
        if not current_user.branch_id:
            raise ForbiddenException("Staff account is not linked to any branch")

        skip = (page - 1) * size
        return BookingRepository.list_by_branch_and_date(
            db=db,
            branch_id=current_user.branch_id,
            target_date=target_date,
            skip=skip,
            limit=size,
        )

    @staticmethod
    def cancel_booking(db: Session, booking_id: int, current_user: User) -> CancelResponse:
        booking = BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise NotFoundException(f"Booking ID {booking_id} not found")

        # Ownership check
        if current_user.role == "CUSTOMER" and booking.customer_id != current_user.id:
            raise ForbiddenException("Access denied: You can only cancel your own bookings")

        if booking.status != BookingStatus.CONFIRMED.value:
            raise BadRequestException(f"Only CONFIRMED bookings can be cancelled (current status: {booking.status})")

        now = datetime.now(timezone.utc)
        pickup_at = booking.pickup_at
        if pickup_at.tzinfo is None:
            pickup_at = pickup_at.replace(tzinfo=timezone.utc)

        # Business Rule 5: Cancellation policy
        # Full refund > 24h before pickup, 50% within 24h, no refund after pickup time has passed
        hours_before_pickup = (pickup_at - now).total_seconds() / 3600.0

        if hours_before_pickup > 24.0:
            refund_amount = booking.estimated_amount + booking.deposit_amount
            message = "Booking cancelled more than 24 hours prior to pickup. Full refund issued."
        elif 0.0 <= hours_before_pickup <= 24.0:
            # 50% of estimated rental + 100% of deposit
            refund_amount = (booking.estimated_amount * Decimal("0.50")) + booking.deposit_amount
            message = "Booking cancelled within 24 hours of pickup. 50% rental refund and full deposit issued."
        else:
            refund_amount = Decimal("0.00")
            message = "Booking cancelled after scheduled pickup time. No refund applicable."

        booking.status = BookingStatus.CANCELLED.value
        booking.refund_amount = refund_amount.quantize(Decimal("0.01"))
        BookingRepository.update(db, booking)

        logger.info(f"AUDIT: Booking {booking.booking_no} cancelled by User {current_user.id}. Refund: {booking.refund_amount}")

        return CancelResponse(
            booking_id=booking.id,
            booking_no=booking.booking_no,
            status=BookingStatus.CANCELLED,
            refund_amount=booking.refund_amount,
            message=message,
        )
