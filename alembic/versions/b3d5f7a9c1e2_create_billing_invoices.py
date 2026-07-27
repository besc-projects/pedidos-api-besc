"""create billing.invoices (nota fiscal — emissão/transmissão)

Revision ID: b3d5f7a9c1e2
Revises: e5a7c1d9f3b2
Create Date: 2026-07-26

Idempotent DDL (IF [NOT] EXISTS) so it applies cleanly whether or not the
objects already exist.
"""

from alembic import op

revision = "b3d5f7a9c1e2"
down_revision = "e5a7c1d9f3b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS billing")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS billing.invoices (
            id                 SERIAL PRIMARY KEY,
            created_at         TIMESTAMPTZ DEFAULT now(),
            updated_at         TIMESTAMPTZ DEFAULT now(),
            order_id           BIGINT NOT NULL
                               REFERENCES core.orders (id) ON DELETE CASCADE,
            supra_id           BIGINT NOT NULL,
            issue_code         VARCHAR(100) NOT NULL,
            transmission_code  VARCHAR(100),
            CONSTRAINT uq_invoice_order UNIQUE (order_id)
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_invoices_order_id "
        "ON billing.invoices (order_id);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS billing.invoices")
