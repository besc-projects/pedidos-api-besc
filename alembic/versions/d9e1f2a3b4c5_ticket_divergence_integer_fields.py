"""ticket divergence integer fields

Revision ID: d9e1f2a3b4c5
Revises: c3d5e7f9a1b3
Create Date: 2026-03-10 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d9e1f2a3b4c5"
down_revision: Union[str, Sequence[str], None] = "c3d5e7f9a1b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("ticket_divergences"):
        return

    has_disputed_table = inspector.has_table("ticket_divergence_disputed_taxes")

    # Drop FK before changing referenced/referencing column types.
    if has_disputed_table:
        op.execute(
            sa.text(
                """
                DO $$
                DECLARE r record;
                BEGIN
                    FOR r IN (
                        SELECT c.conname
                        FROM pg_constraint c
                        JOIN pg_class t ON c.conrelid = t.oid
                        JOIN pg_class rt ON c.confrelid = rt.oid
                        WHERE c.contype = 'f'
                          AND t.relname = 'ticket_divergence_disputed_taxes'
                          AND rt.relname = 'ticket_divergences'
                    ) LOOP
                        EXECUTE format(
                            'ALTER TABLE ticket_divergence_disputed_taxes DROP CONSTRAINT %I',
                            r.conname
                        );
                    END LOOP;
                END $$;
                """
            )
        )

        # Named drop for legacy environments where this FK exists explicitly.
        op.execute(
            sa.text(
                """
                ALTER TABLE ticket_divergence_disputed_taxes
                DROP CONSTRAINT IF EXISTS fk_tax_divergence
                """
            )
        )

        disputed_columns = {
            c["name"]: c
            for c in inspector.get_columns("ticket_divergence_disputed_taxes")
        }
        if "ticket_divergence_item_id" in disputed_columns and not isinstance(
            disputed_columns["ticket_divergence_item_id"]["type"], sa.Integer
        ):
            op.execute(
                sa.text(
                    """
                    ALTER TABLE ticket_divergence_disputed_taxes
                    ALTER COLUMN ticket_divergence_item_id TYPE INTEGER
                    USING ticket_divergence_item_id::INTEGER
                    """
                )
            )

    columns = {c["name"]: c for c in inspector.get_columns("ticket_divergences")}

    if "purchase_order_line" in columns and not isinstance(
        columns["purchase_order_line"]["type"], sa.Integer
    ):
        op.execute(
            sa.text(
                """
                ALTER TABLE ticket_divergences
                ALTER COLUMN purchase_order_line TYPE INTEGER
                USING NULLIF(purchase_order_line, '')::INTEGER
                """
            )
        )

    if "item_id" in columns and not isinstance(columns["item_id"]["type"], sa.Integer):
        op.execute(
            sa.text(
                """
                ALTER TABLE ticket_divergences
                ALTER COLUMN item_id TYPE INTEGER
                USING item_id::INTEGER
                """
            )
        )

    if has_disputed_table:
        op.create_foreign_key(
            "fk_tax_divergence",
            "ticket_divergence_disputed_taxes",
            "ticket_divergences",
            ["ticket_divergence_id", "ticket_divergence_item_id"],
            ["id", "item_id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("ticket_divergences"):
        return

    has_disputed_table = inspector.has_table("ticket_divergence_disputed_taxes")

    if has_disputed_table:
        op.execute(
            sa.text(
                """
                DO $$
                DECLARE r record;
                BEGIN
                    FOR r IN (
                        SELECT c.conname
                        FROM pg_constraint c
                        JOIN pg_class t ON c.conrelid = t.oid
                        JOIN pg_class rt ON c.confrelid = rt.oid
                        WHERE c.contype = 'f'
                          AND t.relname = 'ticket_divergence_disputed_taxes'
                          AND rt.relname = 'ticket_divergences'
                    ) LOOP
                        EXECUTE format(
                            'ALTER TABLE ticket_divergence_disputed_taxes DROP CONSTRAINT %I',
                            r.conname
                        );
                    END LOOP;
                END $$;
                """
            )
        )

    columns = {c["name"]: c for c in inspector.get_columns("ticket_divergences")}

    if "purchase_order_line" in columns and not isinstance(
        columns["purchase_order_line"]["type"], sa.String
    ):
        op.execute(
            sa.text(
                """
                ALTER TABLE ticket_divergences
                ALTER COLUMN purchase_order_line TYPE VARCHAR(50)
                USING purchase_order_line::VARCHAR
                """
            )
        )

    if "item_id" in columns and not isinstance(columns["item_id"]["type"], sa.String):
        op.execute(
            sa.text(
                """
                ALTER TABLE ticket_divergences
                ALTER COLUMN item_id TYPE VARCHAR(50)
                USING item_id::VARCHAR
                """
            )
        )

    if has_disputed_table:
        disputed_columns = {
            c["name"]: c
            for c in inspector.get_columns("ticket_divergence_disputed_taxes")
        }
        if "ticket_divergence_item_id" in disputed_columns and not isinstance(
            disputed_columns["ticket_divergence_item_id"]["type"], sa.String
        ):
            op.execute(
                sa.text(
                    """
                    ALTER TABLE ticket_divergence_disputed_taxes
                    ALTER COLUMN ticket_divergence_item_id TYPE VARCHAR(50)
                    USING ticket_divergence_item_id::VARCHAR
                    """
                )
            )

        op.create_foreign_key(
            "fk_tax_divergence",
            "ticket_divergence_disputed_taxes",
            "ticket_divergences",
            ["ticket_divergence_id", "ticket_divergence_item_id"],
            ["id", "item_id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        )
