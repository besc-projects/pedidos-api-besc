"""create supplies.purchase_requests and drop orders.proposal_id

Revision ID: e5a7c1d9f3b2
Revises: dc97a106f6f2
Create Date: 2026-07-25

Idempotent DDL (IF [NOT] EXISTS) so it applies cleanly whether or not the
objects already exist, since the schema drifted from manual changes in some
environments.
"""

from alembic import op

revision = "e5a7c1d9f3b2"
down_revision = "dc97a106f6f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS supplies")

    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE supplies.purchase_request_status
                AS ENUM ('PENDING', 'COMPLETED');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END
        $$;
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS supplies.purchase_requests (
            id                    SERIAL PRIMARY KEY,
            created_at            TIMESTAMPTZ DEFAULT now(),
            updated_at            TIMESTAMPTZ DEFAULT now(),
            order_id              BIGINT NOT NULL,
            product_id            BIGINT NOT NULL,
            supplier_product_code VARCHAR(100),
            part_number           VARCHAR(100) NOT NULL,
            released_quantity     NUMERIC(12, 2) NOT NULL,
            requested_quantity    NUMERIC(12, 2) NOT NULL,
            status                supplies.purchase_request_status
                                  NOT NULL DEFAULT 'PENDING',
            CONSTRAINT uq_order_part_number UNIQUE (order_id, part_number)
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_supplies_purchase_requests_order_id "
        "ON supplies.purchase_requests (order_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_supplies_purchase_requests_part_number "
        "ON supplies.purchase_requests (part_number);"
    )

    op.execute("ALTER TABLE core.orders DROP COLUMN IF EXISTS proposal_id;")


def downgrade() -> None:
    op.execute(
        "ALTER TABLE core.orders ADD COLUMN IF NOT EXISTS proposal_id INTEGER;"
    )
    op.execute("DROP TABLE IF EXISTS supplies.purchase_requests;")
    op.execute("DROP TYPE IF EXISTS supplies.purchase_request_status;")
