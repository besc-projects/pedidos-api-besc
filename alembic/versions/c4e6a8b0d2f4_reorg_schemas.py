"""reorg schemas: purchasing/identity/pricing + rename tables

Revision ID: c4e6a8b0d2f4
Revises: b3d5f7a9c1e2
Create Date: 2026-07-26

Renomeia/organiza os schemas por domínio (contrato HTTP inalterado):
  - supplies                     -> purchasing            (schema + enum juntos)
  - core.users                   -> identity.users
  - core.price_table             -> pricing.prices
  - core.tax_reference_product_supra -> pricing.tax_references
  - audit.history_process        -> audit.process_history

Guardas IF EXISTS para tolerar drift/reexecução.
"""

from alembic import op

revision = "c4e6a8b0d2f4"
down_revision = "b3d5f7a9c1e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS identity")
    op.execute("CREATE SCHEMA IF NOT EXISTS pricing")

    # supplies -> purchasing (leva a tabela purchase_requests e o enum junto)
    op.execute(
        """
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.schemata
                       WHERE schema_name = 'supplies') THEN
                ALTER SCHEMA supplies RENAME TO purchasing;
            END IF;
        END $$;
        """
    )

    # core.users -> identity.users
    op.execute(
        """
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables
                       WHERE table_schema = 'core' AND table_name = 'users') THEN
                ALTER TABLE core.users SET SCHEMA identity;
            END IF;
        END $$;
        """
    )

    # core.price_table -> pricing.prices
    op.execute(
        """
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables
                       WHERE table_schema = 'core' AND table_name = 'price_table') THEN
                ALTER TABLE core.price_table SET SCHEMA pricing;
                ALTER TABLE pricing.price_table RENAME TO prices;
            END IF;
        END $$;
        """
    )

    # core.tax_reference_product_supra -> pricing.tax_references
    op.execute(
        """
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables
                       WHERE table_schema = 'core'
                         AND table_name = 'tax_reference_product_supra') THEN
                ALTER TABLE core.tax_reference_product_supra SET SCHEMA pricing;
                ALTER TABLE pricing.tax_reference_product_supra RENAME TO tax_references;
            END IF;
        END $$;
        """
    )

    # audit.history_process -> audit.process_history
    op.execute(
        """
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables
                       WHERE table_schema = 'audit' AND table_name = 'history_process') THEN
                ALTER TABLE audit.history_process RENAME TO process_history;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        "DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='audit' AND table_name='process_history') THEN "
        "ALTER TABLE audit.process_history RENAME TO history_process; END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='pricing' AND table_name='tax_references') THEN "
        "ALTER TABLE pricing.tax_references RENAME TO tax_reference_product_supra; "
        "ALTER TABLE pricing.tax_reference_product_supra SET SCHEMA core; END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='pricing' AND table_name='prices') THEN "
        "ALTER TABLE pricing.prices RENAME TO price_table; "
        "ALTER TABLE pricing.price_table SET SCHEMA core; END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='identity' AND table_name='users') THEN "
        "ALTER TABLE identity.users SET SCHEMA core; END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.schemata "
        "WHERE schema_name='purchasing') THEN "
        "ALTER SCHEMA purchasing RENAME TO supplies; END IF; END $$;"
    )
