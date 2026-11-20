"""Remove booking, rental, and invoice tables from the initial-stage schema.

Revision ID: 003_remove_future_stage_tables
Revises: 002_remove_auth_fields
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003_remove_future_stage_tables"
down_revision: Union[str, None] = "002_remove_auth_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    existing_tables = set(sa.inspect(bind).get_table_names())
    if "users" in existing_tables:
        existing_columns = {
            column["name"] for column in sa.inspect(bind).get_columns("users")
        }
        if "licence_verified" in existing_columns:
            with op.batch_alter_table("users") as batch_op:
                batch_op.drop_column("licence_verified")
    for table_name in ("invoices", "rentals", "bookings"):
        if table_name in existing_tables:
            op.drop_table(table_name)


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "licence_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("booking_no", sa.String(length=100), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("pickup_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("drop_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estimated_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("refund_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="CONFIRMED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bookings_id"), "bookings", ["id"], unique=False)
    op.create_index(op.f("ix_bookings_booking_no"), "bookings", ["booking_no"], unique=True)
    op.create_index(
        "ix_bookings_vehicle_pickup_drop",
        "bookings",
        ["vehicle_id", "pickup_at", "drop_at"],
        unique=False,
    )
    op.create_table(
        "rentals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("actual_pickup_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_drop_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("odometer_out", sa.Numeric(12, 2), nullable=False),
        sa.Column("odometer_in", sa.Numeric(12, 2), nullable=True),
        sa.Column("fuel_out", sa.Numeric(12, 2), nullable=False),
        sa.Column("fuel_in", sa.Numeric(12, 2), nullable=True),
        sa.Column("damage_notes", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id"),
    )
    op.create_index(op.f("ix_rentals_id"), "rentals", ["id"], unique=False)
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rental_id", sa.Integer(), nullable=False),
        sa.Column("base_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("extra_km_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("extra_hour_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("fuel_charge", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("damage_charge", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("deposit_adjusted", sa.Numeric(12, 2), nullable=False),
        sa.Column("payable_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["rental_id"], ["rentals.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rental_id"),
    )
    op.create_index(op.f("ix_invoices_id"), "invoices", ["id"], unique=False)
