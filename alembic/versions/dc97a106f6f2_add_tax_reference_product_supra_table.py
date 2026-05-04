"""add_tax_reference_product_supra_table

Revision ID: dc97a106f6f2
Revises: e4f6a8b0c2d4
Create Date: 2026-05-04 12:15:59.980432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'dc97a106f6f2'
down_revision: Union[str, Sequence[str], None] = 'e4f6a8b0c2d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS tax_reference_product_supra (
            id BIGSERIAL PRIMARY KEY,
            id_product INTEGER NOT NULL,
            ncm_code VARCHAR(10) NOT NULL,
            ipi NUMERIC(5,2),
            icms NUMERIC(5,2),
            icms_st NUMERIC(5,2),
            origin VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_tax_reference_product_supra_id_product "
        "ON tax_reference_product_supra (id_product)"
    )


def downgrade() -> None:
    op.drop_table('tax_reference_product_supra')
