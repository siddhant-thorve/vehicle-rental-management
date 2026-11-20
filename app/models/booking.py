from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import BookingStatus
from app.models.mixins import TimestampMixin

class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_no: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), nullable=False)
    pickup_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    drop_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estimated_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    deposit_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    refund_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False)

    __table_args__ = (
        Index("ix_bookings_vehicle_window", "vehicle_id", "pickup_at", "drop_at"),
    )

    customer = relationship("User", back_populates="bookings")
    vehicle = relationship("Vehicle", back_populates="bookings")
    branch = relationship("Branch", back_populates="bookings")
    rental = relationship("Rental", back_populates="booking", uselist=False)
