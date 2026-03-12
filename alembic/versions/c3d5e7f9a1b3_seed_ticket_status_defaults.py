"""seed default ticket statuses

Revision ID: c3d5e7f9a1b3
Revises: b2c4d6e8f0a1
Create Date: 2026-03-09 00:00:03.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3d5e7f9a1b3"
down_revision: Union[str, Sequence[str], None] = "b2c4d6e8f0a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("tickets_status"):
        return

    columns = {column["name"] for column in inspector.get_columns("tickets_status")}

    if "name" not in columns:
        op.add_column("tickets_status", sa.Column("name", sa.String(length=255), nullable=True))

    if "description" not in columns:
        op.add_column(
            "tickets_status",
            sa.Column("description", sa.String(length=255), nullable=True),
        )

    op.execute(
        sa.text(
            """
            INSERT INTO tickets_status (id, name, description)
            VALUES
                (0, 'EM_ABERTO', 'Em aberto'),
                (1, 'EM_ANDAMENTO', 'Em andamento'),
                (2, 'CONCLUIDO', 'Concluido'),
                (3, 'REABERTO', 'Reaberto')
            ON CONFLICT (id)
            DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("tickets_status"):
        return

    op.execute(sa.text("DELETE FROM tickets_status WHERE id IN (0, 1, 2, 3)"))
