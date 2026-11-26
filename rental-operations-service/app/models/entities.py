from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from app.db.base import Base


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, unique=True, nullable=False)
    actual_pickup_at = Column(DateTime(timezone=True), nullable=False)
    actual_drop_at = Column(DateTime(timezone=True), nullable=True)
    odometer_out = Column(Numeric(12, 2), nullable=False)
    odometer_in = Column(Numeric(12, 2), nullable=True)
    fuel_out = Column(Numeric(12, 2), nullable=False)
    fuel_in = Column(Numeric(12, 2), nullable=True)
    damage_notes = Column(String(1000), nullable=True)
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


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), unique=True, nullable=False)
    base_amount = Column(Numeric(12, 2), nullable=False)
    extra_km_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    extra_hour_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    fuel_charge = Column(Numeric(12, 2), default=0.00, nullable=False)
    damage_charge = Column(Numeric(12, 2), default=0.00, nullable=False)
    tax_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    deposit_adjusted = Column(Numeric(12, 2), nullable=False)
    payable_amount = Column(Numeric(12, 2), nullable=False)
    generated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
