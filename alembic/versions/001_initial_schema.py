"""Initial schema build from empty

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-19 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. branches
    op.create_table(
        "branches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("contact_no", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_branches_id"), "branches", ["id"], unique=False)
    op.create_index(op.f("ix_branches_city"), "branches", ["city"], unique=False)

    # 2. users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=False),
        sa.Column("licence_no", sa.String(length=100), nullable=True),
        sa.Column("licence_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # 3. vehicle_categories
    op.create_table(
        "vehicle_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("seating_capacity", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_vehicle_categories_id"), "vehicle_categories", ["id"], unique=False)

    # 4. vehicles
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("registration_no", sa.String(length=100), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("make", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("fuel_type", sa.String(length=50), nullable=False),
        sa.Column("transmission", sa.String(length=50), nullable=False),
        sa.Column("odometer_km", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="AVAILABLE"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["vehicle_categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vehicles_id"), "vehicles", ["id"], unique=False)
    op.create_index(op.f("ix_vehicles_registration_no"), "vehicles", ["registration_no"], unique=True)

    # 5. tariffs
    op.create_table(
        "tariffs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("hourly_rate", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("daily_rate", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("weekly_rate", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("free_km_per_day", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("extra_km_rate", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("extra_hour_rate", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["vehicle_categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tariffs_id"), "tariffs", ["id"], unique=False)

    # 6. bookings
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
        sa.Column("refund_amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
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
    op.create_index("ix_bookings_vehicle_pickup_drop", "bookings", ["vehicle_id", "pickup_at", "drop_at"], unique=False)

    # 7. rentals
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
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id"),
    )
    op.create_index(op.f("ix_rentals_id"), "rentals", ["id"], unique=False)

    # 8. invoices
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rental_id", sa.Integer(), nullable=False),
        sa.Column("base_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("extra_km_amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
        sa.Column("extra_hour_amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
        sa.Column("fuel_charge", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
        sa.Column("damage_charge", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
        sa.Column("tax_amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
        sa.Column("total_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("deposit_adjusted", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("payable_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["rental_id"], ["rentals.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rental_id"),
    )
    op.create_index(op.f("ix_invoices_id"), "invoices", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_invoices_id"), table_name="invoices")
    op.drop_table("invoices")
    op.drop_index(op.f("ix_rentals_id"), table_name="rentals")
    op.drop_table("rentals")
    op.drop_index("ix_bookings_vehicle_pickup_drop", table_name="bookings")
    op.drop_index(op.f("ix_bookings_booking_no"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_id"), table_name="bookings")
    op.drop_table("bookings")
    op.drop_index(op.f("ix_tariffs_id"), table_name="tariffs")
    op.drop_table("tariffs")
    op.drop_index(op.f("ix_vehicles_registration_no"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_id"), table_name="vehicles")
    op.drop_table("vehicles")
    op.drop_index(op.f("ix_vehicle_categories_id"), table_name="vehicle_categories")
    op.drop_table("vehicle_categories")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_branches_city"), table_name="branches")
    op.drop_index(op.f("ix_branches_id"), table_name="branches")
    op.drop_table("branches")
