from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import Booking
from app.repositories.booking import (
    get_booking,
    list_report_bookings as repository_list_report_bookings,
    update_booking_status as repository_update_booking_status,
)


def update_status(db: Session, booking: Booking, new_status: str) -> Booking:
    allowed_transitions = {
        "CONFIRMED": {"IN_PROGRESS"},
        "IN_PROGRESS": {"COMPLETED"},
    }
    if new_status not in allowed_transitions.get(booking.status, set()):
        raise ValueError(f"Cannot change booking status from {booking.status} to {new_status}")
    return repository_update_booking_status(db, booking, new_status)


def get_booking_record(db: Session, booking_id: int) -> Booking | None:
    return get_booking(db, booking_id)


def list_report_bookings(
    db: Session, branch_id: int, start_at: datetime, end_at: datetime
) -> list[Booking]:
    return repository_list_report_bookings(db, branch_id, start_at, end_at)
