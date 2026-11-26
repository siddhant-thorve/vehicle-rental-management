from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.entities import Booking


def has_booking_overlap(
    db: Session, vehicle_id: int, pickup_at: datetime, drop_at: datetime
) -> bool:
    return (
        db.query(Booking)
        .filter(
            Booking.vehicle_id == vehicle_id,
            Booking.status.in_(["CONFIRMED", "IN_PROGRESS"]),
            Booking.pickup_at < drop_at,
            Booking.drop_at > pickup_at,
        )
        .first()
        is not None
    )


def create_booking(db: Session, booking: Booking) -> Booking:
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def list_customer_bookings(db: Session, customer_id: int) -> list[Booking]:
    return (
        db.query(Booking)
        .filter(Booking.customer_id == customer_id)
        .order_by(Booking.id.desc())
        .all()
    )


def get_booking(db: Session, booking_id: int) -> Booking | None:
    return db.query(Booking).filter(Booking.id == booking_id).first()


def cancel_booking(db: Session, booking: Booking, refund_amount: Decimal) -> Booking:
    booking.status = "CANCELLED"
    booking.refund_amount = refund_amount
    db.commit()
    db.refresh(booking)
    return booking


def list_branch_bookings(
    db: Session,
    branch_id: Optional[int],
    start_at: Optional[datetime],
    end_at: Optional[datetime],
) -> list[Booking]:
    query = db.query(Booking)
    if branch_id is not None:
        query = query.filter(Booking.branch_id == branch_id)
    if start_at is not None and end_at is not None:
        query = query.filter(Booking.pickup_at >= start_at, Booking.pickup_at <= end_at)
    return query.order_by(Booking.pickup_at.asc()).all()


def update_booking_status(db: Session, booking: Booking, new_status: str) -> Booking:
    booking.status = new_status
    db.commit()
    db.refresh(booking)
    return booking


def list_report_bookings(
    db: Session, branch_id: int, start_at: datetime, end_at: datetime
) -> list[Booking]:
    return (
        db.query(Booking)
        .filter(
            Booking.branch_id == branch_id,
            Booking.status.in_(["CONFIRMED", "IN_PROGRESS", "COMPLETED"]),
            Booking.pickup_at <= end_at,
            Booking.drop_at >= start_at,
        )
        .all()
    )
