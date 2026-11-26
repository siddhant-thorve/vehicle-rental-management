"""Create Catalog Service tables.

Revision ID: catalog_20261126_01
Revises:
Create Date: 2026-11-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "catalog_20261126_01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicle_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("seating_capacity", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_vehicle_categories_id",
        "vehicle_categories",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_vehicle_categories_name",
        "vehicle_categories",
        ["name"],
        unique=True,
    )

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
        sa.ForeignKeyConstraint(["category_id"], ["vehicle_categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tariffs_id", "tariffs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tariffs_id", table_name="tariffs")
    op.drop_table("tariffs")
    op.drop_index("ix_vehicle_categories_name", table_name="vehicle_categories")
    op.drop_index("ix_vehicle_categories_id", table_name="vehicle_categories")
    op.drop_table("vehicle_categories")
