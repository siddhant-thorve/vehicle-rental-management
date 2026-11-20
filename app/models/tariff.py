from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, Numeric, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from app.db.base import Base, TimestampMixin


class Tariff(Base, TimestampMixin):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicle_categories.id"), nullable=False)
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    daily_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    weekly_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    free_km_per_day: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    extra_km_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    extra_hour_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    deposit_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    category = relationship("VehicleCategory", back_populates="tariffs")
