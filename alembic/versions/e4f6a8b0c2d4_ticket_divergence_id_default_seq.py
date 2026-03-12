"""ticket divergence id default sequence

Revision ID: e4f6a8b0c2d4
Revises: d9e1f2a3b4c5
Create Date: 2026-03-10 00:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4f6a8b0c2d4"
down_revision: Union[str, Sequence[str], None] = "d9e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("ticket_divergences"):
        return

    columns = {c["name"]: c for c in inspector.get_columns("ticket_divergences")}
    id_col = columns.get("id")
    if not id_col:
        return

    if not isinstance(id_col["type"], sa.Integer):
        return

    op.execute(
        sa.text(
            """
            CREATE SEQUENCE IF NOT EXISTS ticket_divergences_id_seq
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE ticket_divergences
            ALTER COLUMN id SET DEFAULT nextval('ticket_divergences_id_seq')
            """
        )
    )

    op.execute(
        sa.text(
            """
            SELECT setval(
                'ticket_divergences_id_seq',
                COALESCE((SELECT MAX(id) FROM ticket_divergences), 0),
                true
            )
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("ticket_divergences"):
        return

    columns = {c["name"]: c for c in inspector.get_columns("ticket_divergences")}
    id_col = columns.get("id")
    if not id_col:
        return

    if isinstance(id_col["type"], sa.Integer):
        op.execute(
            sa.text(
                """
                ALTER TABLE ticket_divergences
                ALTER COLUMN id DROP DEFAULT
                """
            )
        )

    op.execute(sa.text("DROP SEQUENCE IF EXISTS ticket_divergences_id_seq"))
