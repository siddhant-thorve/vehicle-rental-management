from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, Numeric, String

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_no = Column(String(100), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, nullable=False, index=True)
    vehicle_id = Column(Integer, nullable=False, index=True)
    branch_id = Column(Integer, nullable=False, index=True)
    pickup_at = Column(DateTime(timezone=True), nullable=False)
    drop_at = Column(DateTime(timezone=True), nullable=False)
    estimated_amount = Column(Numeric(12, 2), nullable=False)
    deposit_amount = Column(Numeric(12, 2), nullable=False)
    refund_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    status = Column(String(50), default="CONFIRMED", nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
