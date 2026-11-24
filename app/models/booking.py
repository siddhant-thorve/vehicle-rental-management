from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, Numeric, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from typing import Optional
from app.db.base import Base, TimestampMixin


class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_no: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"), nullable=False)
    pickup_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    drop_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estimated_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    deposit_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="CONFIRMED", nullable=False)  # CONFIRMED, CANCELLED, IN_PROGRESS, COMPLETED

    # Relationships
    customer = relationship("User", back_populates="bookings")
    vehicle = relationship("Vehicle", back_populates="bookings")
    branch = relationship("Branch", back_populates="bookings")
    rental = relationship("Rental", back_populates="booking", uselist=False)

    __table_args__ = (
        Index("ix_bookings_vehicle_pickup_drop", "vehicle_id", "pickup_at", "drop_at"),
    )
