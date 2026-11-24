from datetime import datetime, date, time
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, and_
from app.models.booking import Booking


class BookingRepository:
    @staticmethod
    def get_by_id(db: Session, booking_id: int) -> Optional[Booking]:
        return db.get(Booking, booking_id)

    @staticmethod
    def get_by_booking_no(db: Session, booking_no: str) -> Optional[Booking]:
        stmt = select(Booking).where(Booking.booking_no == booking_no)
        return db.scalars(stmt).first()

    @staticmethod
    def create(db: Session, booking: Booking) -> Booking:
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def update(db: Session, booking: Booking) -> Booking:
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def has_overlap(
        db: Session,
        vehicle_id: int,
        pickup_at: datetime,
        drop_at: datetime,
        exclude_booking_id: Optional[int] = None,
    ) -> bool:
        stmt = select(Booking).where(
            Booking.vehicle_id == vehicle_id,
            Booking.status.in_(["CONFIRMED", "IN_PROGRESS"]),
            Booking.pickup_at < drop_at,
            Booking.drop_at > pickup_at,
        )
        if exclude_booking_id:
            stmt = stmt.where(Booking.id != exclude_booking_id)
        
        overlapping = db.scalars(stmt).first()
        return overlapping is not None

    @staticmethod
    def list_by_customer(
        db: Session,
        customer_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Booking], int]:
        stmt = select(Booking).where(Booking.customer_id == customer_id)
        count_stmt = select(func.count(Booking.id)).where(Booking.customer_id == customer_id)

        if status:
            stmt = stmt.where(Booking.status == status)
            count_stmt = count_stmt.where(Booking.status == status)

        stmt = stmt.order_by(desc(Booking.created_at))
        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.offset(skip).limit(limit)).all())
        return items, total

    @staticmethod
    def list_by_branch_and_date(
        db: Session,
        branch_id: int,
        target_date: date,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Booking], int]:
        start_of_day = datetime.combine(target_date, time.min)
        end_of_day = datetime.combine(target_date, time.max)

        stmt = select(Booking).where(
            Booking.branch_id == branch_id,
            Booking.pickup_at <= end_of_day,
            Booking.drop_at >= start_of_day,
        )
        count_stmt = select(func.count(Booking.id)).where(
            Booking.branch_id == branch_id,
            Booking.pickup_at <= end_of_day,
            Booking.drop_at >= start_of_day,
        )

        stmt = stmt.order_by(desc(Booking.pickup_at))
        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.offset(skip).limit(limit)).all())
        return items, total
