"""index products.order_id

Revision ID: c8a2e6f4b1d3
Revises: b4f0c5bc9239
Create Date: 2026-09-17 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c8a2e6f4b1d3"
down_revision: Union[str, Sequence[str], None] = "b4f0c5bc9239"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("products", schema="core"):
        return

    indexes = {index["name"] for index in inspector.get_indexes("products", schema="core")}
    if "ix_core_products_order_id" not in indexes:
        op.create_index(
            "ix_core_products_order_id", "products", ["order_id"],
            unique=False, schema="core",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("products", schema="core"):
        return

    indexes = {index["name"] for index in inspector.get_indexes("products", schema="core")}
    if "ix_core_products_order_id" in indexes:
        op.drop_index("ix_core_products_order_id", table_name="products", schema="core")
