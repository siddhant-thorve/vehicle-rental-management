from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String

from app.db.base import Base


class VehicleCategory(Base):
    __tablename__ = "vehicle_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    seating_capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(
        Integer, ForeignKey("vehicle_categories.id"), nullable=False
    )
    hourly_rate = Column(Numeric(12, 2), nullable=False)
    daily_rate = Column(Numeric(12, 2), nullable=False)
    weekly_rate = Column(Numeric(12, 2), nullable=False)
    free_km_per_day = Column(Numeric(12, 2), nullable=False)
    extra_km_rate = Column(Numeric(12, 2), nullable=False)
    extra_hour_rate = Column(Numeric(12, 2), nullable=False)
    deposit_amount = Column(Numeric(12, 2), nullable=False)
    effective_from = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
