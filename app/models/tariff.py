from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy import Numeric

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Tariff(Base, TimestampMixin):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_categories.id")
    )

    hourly_rate: Mapped[Decimal] = mapped_column(
        Numeric(12, 2)
    )

    daily_rate: Mapped[Decimal] = mapped_column(
        Numeric(12, 2)
    )