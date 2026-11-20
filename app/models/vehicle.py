from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import FuelType, TransmissionType, VehicleStatus
from app.models.mixins import TimestampMixin

class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    registration_no: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("vehicle_categories.id"), nullable=False)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), nullable=False)
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    fuel_type: Mapped[FuelType] = mapped_column(Enum(FuelType), nullable=False)
    transmission: Mapped[TransmissionType] = mapped_column(Enum(TransmissionType), nullable=False)
    odometer_km: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[VehicleStatus] = mapped_column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE, nullable=False)

    category = relationship("VehicleCategory", back_populates="vehicles")
    branch = relationship("Branch", back_populates="vehicles")
    bookings = relationship("Booking", back_populates="vehicle")
