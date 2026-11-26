"""Create Booking Service table.

Revision ID: booking_20261126_01
Revises:
Create Date: 2026-11-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "booking_20261126_01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("booking_no", sa.String(length=100), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("pickup_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("drop_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estimated_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("refund_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bookings_id", "bookings", ["id"], unique=False)
    op.create_index(
        "ix_bookings_booking_no", "bookings", ["booking_no"], unique=True
    )
    op.create_index(
        "ix_bookings_customer_id", "bookings", ["customer_id"], unique=False
    )
    op.create_index(
        "ix_bookings_vehicle_id", "bookings", ["vehicle_id"], unique=False
    )
    op.create_index(
        "ix_bookings_branch_id", "bookings", ["branch_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_bookings_branch_id", table_name="bookings")
    op.drop_index("ix_bookings_vehicle_id", table_name="bookings")
    op.drop_index("ix_bookings_customer_id", table_name="bookings")
    op.drop_index("ix_bookings_booking_no", table_name="bookings")
    op.drop_index("ix_bookings_id", table_name="bookings")
    op.drop_table("bookings")
