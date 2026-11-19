from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class VehicleCategory(Base, TimestampMixin):
    __tablename__ = "vehicle_categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True
    )

    description: Mapped[str] = mapped_column(
        String(255)
    )