from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    DateTime,
    Numeric,
    Enum,
    Index
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.base import Base

from app.models.mixins import TimestampMixin

from app.models.enums import BookingStatus


class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id")
    )

    pickup_at: Mapped = mapped_column(
        DateTime(timezone=True)
    )

    drop_at: Mapped = mapped_column(
        DateTime(timezone=True)
    )

    estimated_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2)
    )

    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus)
    )

    __table_args__ = (
        Index(
            "idx_booking_overlap",
            "vehicle_id",
            "pickup_at",
            "drop_at"
        ),
    )