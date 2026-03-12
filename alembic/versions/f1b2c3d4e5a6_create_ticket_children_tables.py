"""create ticket children tables

Revision ID: f1b2c3d4e5a6
Revises: d4a8e1f9b2c7
Create Date: 2026-03-09 00:00:01.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f1b2c3d4e5a6"
down_revision: Union[str, Sequence[str], None] = "d4a8e1f9b2c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("ticket_progresses"):
        op.create_table(
            "ticket_progresses",
            sa.Column("id", sa.String(length=50), nullable=False),
            sa.Column("ticket_id", sa.Integer(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("start_date", sa.DateTime(), nullable=True),
            sa.Column("end_date", sa.DateTime(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(
                ["ticket_id"],
                ["tickets.id"],
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("ticket_divergences"):
        op.create_table(
            "ticket_divergences",
            sa.Column("id", sa.String(length=50), nullable=False),
            sa.Column("item_id", sa.String(length=50), nullable=False),
            sa.Column("ticket_id", sa.Integer(), nullable=False),
            sa.Column("status_id", sa.Integer(), nullable=False),
            sa.Column("legal_basis", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(
                ["status_id"],
                ["tickets_status.id"],
                onupdate="CASCADE",
                ondelete="RESTRICT",
            ),
            sa.ForeignKeyConstraint(
                ["ticket_id"],
                ["tickets.id"],
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id", "item_id"),
        )

    if not inspector.has_table("ticket_divergence_disputed_taxes"):
        op.create_table(
            "ticket_divergence_disputed_taxes",
            sa.Column("id", sa.String(length=50), nullable=False),
            sa.Column("ticket_divergence_id", sa.String(length=50), nullable=False),
            sa.Column(
                "ticket_divergence_item_id", sa.String(length=50), nullable=False
            ),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(
                ["ticket_divergence_id", "ticket_divergence_item_id"],
                ["ticket_divergences.id", "ticket_divergences.item_id"],
                onupdate="CASCADE",
                ondelete="CASCADE",
                name="fk_tax_divergence",
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    indexes_progress = {idx["name"] for idx in inspector.get_indexes("ticket_progresses")} if inspector.has_table("ticket_progresses") else set()
    if "idx_progress_ticket" not in indexes_progress:
        op.create_index(
            "idx_progress_ticket",
            "ticket_progresses",
            ["ticket_id"],
            unique=False,
        )

    indexes_divergence = {idx["name"] for idx in inspector.get_indexes("ticket_divergences")} if inspector.has_table("ticket_divergences") else set()
    if "idx_divergence_ticket" not in indexes_divergence:
        op.create_index(
            "idx_divergence_ticket",
            "ticket_divergences",
            ["ticket_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("ticket_divergences"):
        indexes_divergence = {idx["name"] for idx in inspector.get_indexes("ticket_divergences")}
        if "idx_divergence_ticket" in indexes_divergence:
            op.drop_index("idx_divergence_ticket", table_name="ticket_divergences")

    if inspector.has_table("ticket_progresses"):
        indexes_progress = {idx["name"] for idx in inspector.get_indexes("ticket_progresses")}
        if "idx_progress_ticket" in indexes_progress:
            op.drop_index("idx_progress_ticket", table_name="ticket_progresses")

    if inspector.has_table("ticket_divergence_disputed_taxes"):
        op.drop_table("ticket_divergence_disputed_taxes")

    if inspector.has_table("ticket_divergences"):
        op.drop_table("ticket_divergences")

    if inspector.has_table("ticket_progresses"):
        op.drop_table("ticket_progresses")
