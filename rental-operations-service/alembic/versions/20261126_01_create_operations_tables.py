"""Create Rental Operations Service tables.

Revision ID: operations_20261126_01
Revises:
Create Date: 2026-11-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "operations_20261126_01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rentals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("actual_pickup_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_drop_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("odometer_out", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("odometer_in", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("fuel_out", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("fuel_in", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("damage_notes", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id"),
    )
    op.create_index("ix_rentals_id", "rentals", ["id"], unique=False)

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rental_id", sa.Integer(), nullable=False),
        sa.Column("base_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("extra_km_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("extra_hour_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("fuel_charge", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("damage_charge", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("deposit_adjusted", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("payable_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["rental_id"], ["rentals.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rental_id"),
    )
    op.create_index("ix_invoices_id", "invoices", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_invoices_id", table_name="invoices")
    op.drop_table("invoices")
    op.drop_index("ix_rentals_id", table_name="rentals")
    op.drop_table("rentals")
