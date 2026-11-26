from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from app.db.base import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    contact_no = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    registration_no = Column(String(50), unique=True, index=True, nullable=False)
    category_id = Column(Integer, nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    fuel_type = Column(String(20), nullable=False)  # Petrol, Diesel, Electric
    transmission = Column(String(20), nullable=False)  # Manual, Automatic
    odometer_km = Column(Numeric(12, 2), default=0.0, nullable=False)
    status = Column(String(30), default="AVAILABLE", nullable=False)  # AVAILABLE, BOOKED, UNDER_MAINTENANCE, RETIRED
    is_active = Column(Boolean, default=True, nullable=False)
