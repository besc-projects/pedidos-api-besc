"""ticket new flow fields

Revision ID: d4a8e1f9b2c7
Revises: c9f3a1b2d4e6
Create Date: 2026-03-09 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4a8e1f9b2c7"
down_revision: Union[str, Sequence[str], None] = "c9f3a1b2d4e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add fields required by the new ticket flow and relax order linkage."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("tickets"):
        return

    columns = {column["name"] for column in inspector.get_columns("tickets")}

    if "purchase_order" not in columns:
        op.add_column("tickets", sa.Column("purchase_order", sa.String(length=255), nullable=True))

    if "filtered_date" not in columns:
        op.add_column("tickets", sa.Column("filtered_date", sa.DateTime(), nullable=True))

    if "order_id" in columns:
        op.alter_column("tickets", "order_id", existing_type=sa.Integer(), nullable=True)

    indexes = {index["name"] for index in inspector.get_indexes("tickets")}
    if "ix_tickets_ticket_number" not in indexes:
        op.create_index(
            "ix_tickets_ticket_number", "tickets", ["ticket_number"], unique=True
        )


def downgrade() -> None:
    """Rollback fields from the new ticket flow."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("tickets"):
        return

    indexes = {index["name"] for index in inspector.get_indexes("tickets")}
    if "ix_tickets_ticket_number" in indexes:
        op.drop_index("ix_tickets_ticket_number", table_name="tickets")

    columns = {column["name"] for column in inspector.get_columns("tickets")}

    if "filtered_date" in columns:
        op.drop_column("tickets", "filtered_date")

    if "purchase_order" in columns:
        op.drop_column("tickets", "purchase_order")

    if "order_id" in columns:
        op.alter_column("tickets", "order_id", existing_type=sa.Integer(), nullable=False)
