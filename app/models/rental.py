from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from typing import Optional
from app.db.base import Base, TimestampMixin


class Rental(Base, TimestampMixin):
    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    actual_pickup_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_drop_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    odometer_out: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    odometer_in: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    fuel_out: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)  # fuel percentage/litres
    fuel_in: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    damage_notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Relationships
    booking = relationship("Booking", back_populates="rental")
    invoice = relationship("Invoice", back_populates="rental", uselist=False)
