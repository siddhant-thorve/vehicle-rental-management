from datetime import datetime, UTC
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.mixins import TimestampMixin

class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rental_id: Mapped[int] = mapped_column(ForeignKey("rentals.id"), unique=True, nullable=False)
    base_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    extra_km_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    extra_hour_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fuel_charge: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    damage_charge: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    deposit_adjusted: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payable_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    rental = relationship("Rental", back_populates="invoice")
