"""add_history_process_table

Revision ID: a1b2c3d4e5f6
Revises: 584f9e9c886c
Create Date: 2026-02-09 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "584f9e9c886c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria a tabela history_process."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("history_process"):
        op.create_table(
            "history_process",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("orders", sa.String(length=64), nullable=False),
            sa.Column("step", sa.String(length=20), nullable=False),
            sa.Column("id_situation", sa.Integer(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "orders", "step", "id_situation", name="uq_orders_step_situation"
            ),
        )


def downgrade() -> None:
    """Remove a tabela history_process."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("history_process"):
        op.drop_table("history_process")
