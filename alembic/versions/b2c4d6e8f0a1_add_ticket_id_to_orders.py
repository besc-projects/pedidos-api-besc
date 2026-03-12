"""add ticket_id to orders

Revision ID: b2c4d6e8f0a1
Revises: f1b2c3d4e5a6
Create Date: 2026-03-09 00:00:02.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2c4d6e8f0a1"
down_revision: Union[str, Sequence[str], None] = "f1b2c3d4e5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("orders"):
        return

    columns = {column["name"] for column in inspector.get_columns("orders")}
    if "ticket_id" not in columns:
        op.add_column("orders", sa.Column("ticket_id", sa.Integer(), nullable=True))

    indexes = {index["name"] for index in inspector.get_indexes("orders")}
    if "ix_orders_ticket_id" not in indexes:
        op.create_index("ix_orders_ticket_id", "orders", ["ticket_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("orders"):
        return

    indexes = {index["name"] for index in inspector.get_indexes("orders")}
    if "ix_orders_ticket_id" in indexes:
        op.drop_index("ix_orders_ticket_id", table_name="orders")

    columns = {column["name"] for column in inspector.get_columns("orders")}
    if "ticket_id" in columns:
        op.drop_column("orders", "ticket_id")
