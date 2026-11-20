from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.mixins import TimestampMixin

class VehicleCategory(Base, TimestampMixin):
    __tablename__ = "vehicle_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    seating_capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    vehicles = relationship("Vehicle", back_populates="category")
    tariffs = relationship("Tariff", back_populates="category")
