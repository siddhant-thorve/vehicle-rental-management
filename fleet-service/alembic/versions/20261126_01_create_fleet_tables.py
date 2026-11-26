"""Create Fleet Service tables.

Revision ID: fleet_20261126_01
Revises:
Create Date: 2026-11-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fleet_20261126_01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "branches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("city", sa.String(length=50), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("contact_no", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_branches_id", "branches", ["id"], unique=False)
    op.create_index("ix_branches_city", "branches", ["city"], unique=False)

    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("registration_no", sa.String(length=50), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("make", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=50), nullable=False),
        sa.Column("fuel_type", sa.String(length=20), nullable=False),
        sa.Column("transmission", sa.String(length=20), nullable=False),
        sa.Column("odometer_km", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vehicles_id", "vehicles", ["id"], unique=False)
    op.create_index(
        "ix_vehicles_registration_no",
        "vehicles",
        ["registration_no"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_vehicles_registration_no", table_name="vehicles")
    op.drop_index("ix_vehicles_id", table_name="vehicles")
    op.drop_table("vehicles")
    op.drop_index("ix_branches_city", table_name="branches")
    op.drop_index("ix_branches_id", table_name="branches")
    op.drop_table("branches")
