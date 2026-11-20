from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.mixins import TimestampMixin

class Rental(Base, TimestampMixin):
    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), unique=True, nullable=False)
    actual_pickup_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_drop_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    odometer_out: Mapped[int] = mapped_column(Integer, nullable=False)
    odometer_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel_out: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    fuel_in: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    damage_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    booking = relationship("Booking", back_populates="rental")
    invoice = relationship("Invoice", back_populates="rental", uselist=False)
