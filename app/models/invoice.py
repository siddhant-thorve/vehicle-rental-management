from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Numeric
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)

    rental_id: Mapped[int] = mapped_column(
        ForeignKey("rentals.id")
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2)
    )

    tax: Mapped[Decimal] = mapped_column(
        Numeric(12, 2)
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2)
    )