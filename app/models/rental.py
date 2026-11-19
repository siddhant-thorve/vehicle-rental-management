from sqlalchemy import (
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Rental(Base, TimestampMixin):
    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(primary_key=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id")
    )

    actual_pickup_at: Mapped = mapped_column(
        DateTime(timezone=True)
    )

    actual_return_at: Mapped = mapped_column(
        DateTime(timezone=True)
    )