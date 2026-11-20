from sqlalchemy import Integer, String, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.db.base import Base, TimestampMixin


class VehicleCategory(Base, TimestampMixin):
    __tablename__ = "vehicle_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # Hatchback, SUV, Scooter, etc.
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    seating_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    vehicles = relationship("Vehicle", back_populates="category")
    tariffs = relationship("Tariff", back_populates="category")


class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    registration_no: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicle_categories.id"), nullable=False)
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"), nullable=False)
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Petrol, Diesel, Electric
    transmission: Mapped[str] = mapped_column(String(50), nullable=False)  # Manual, Automatic
    odometer_km: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="AVAILABLE")  # AVAILABLE, BOOKED, UNDER_MAINTENANCE, RETIRED
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    category = relationship("VehicleCategory", back_populates="vehicles")
    branch = relationship("Branch", back_populates="vehicles")
    bookings = relationship("Booking", back_populates="vehicle")
