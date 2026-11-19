from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Enum

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base

from app.models.enums import (
    FuelType,
    TransmissionType,
    VehicleStatus
)

from app.models.mixins import TimestampMixin


class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)

    registration_number: Mapped[str] = mapped_column(
        String(30),
        unique=True
    )

    make: Mapped[str] = mapped_column(String(50))

    model: Mapped[str] = mapped_column(String(50))

    year: Mapped[int]

    fuel_type: Mapped[FuelType] = mapped_column(
        Enum(FuelType)
    )

    transmission: Mapped[TransmissionType] = mapped_column(
        Enum(TransmissionType)
    )

    status: Mapped[VehicleStatus] = mapped_column(
        Enum(VehicleStatus)
    )

    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id")
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_categories.id")
    )

    branch = relationship("Branch")

    category = relationship("VehicleCategory")