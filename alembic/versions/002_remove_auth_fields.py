"""Remove credential and staff-role fields from customer records.

Revision ID: 002_remove_auth_fields
Revises: 001_initial_schema
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_remove_auth_fields"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    existing_columns = {
        column["name"] for column in sa.inspect(bind).get_columns("users")
    }
    columns_to_remove = {"password_hash", "role", "branch_id"} & existing_columns
    if columns_to_remove:
        with op.batch_alter_table("users") as batch_op:
            for column in ("password_hash", "role", "branch_id"):
                if column in columns_to_remove:
                    batch_op.drop_column(column)


def downgrade() -> None:
    bind = op.get_bind()
    existing_columns = {
        column["name"] for column in sa.inspect(bind).get_columns("users")
    }
    with op.batch_alter_table("users") as batch_op:
        if "password_hash" not in existing_columns:
            batch_op.add_column(sa.Column("password_hash", sa.String(length=255), nullable=True))
        if "role" not in existing_columns:
            batch_op.add_column(sa.Column("role", sa.String(length=50), nullable=True))
        if "branch_id" not in existing_columns:
            batch_op.add_column(sa.Column("branch_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_users_branch_id_branches",
                "branches",
                ["branch_id"],
                ["id"],
            )
