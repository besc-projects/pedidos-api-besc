"""price_table unique pn+destination

Revision ID: c9f3a1b2d4e6
Revises: a1b2c3d4e5f6
Create Date: 2026-02-20 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c9f3a1b2d4e6"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Switch uniqueness from pn to pn+destination."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("price_table"):
        return

    indexes = {idx["name"]: idx for idx in inspector.get_indexes("price_table")}
    ix_pn = indexes.get("ix_price_table_pn")

    # Force ix_price_table_pn to be non-unique.
    if ix_pn and ix_pn.get("unique"):
        op.drop_index("ix_price_table_pn", table_name="price_table")
        op.create_index("ix_price_table_pn", "price_table", ["pn"], unique=False)
    elif not ix_pn:
        op.create_index("ix_price_table_pn", "price_table", ["pn"], unique=False)

    unique_constraints = {
        uq["name"]
        for uq in inspector.get_unique_constraints("price_table")
        if uq.get("name")
    }

    if "uq_price_table_pn_destination" not in unique_constraints:
        op.create_unique_constraint(
            "uq_price_table_pn_destination", "price_table", ["pn", "destination"]
        )


def downgrade() -> None:
    """Restore uniqueness on pn only."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("price_table"):
        return

    unique_constraints = {
        uq["name"]
        for uq in inspector.get_unique_constraints("price_table")
        if uq.get("name")
    }
    if "uq_price_table_pn_destination" in unique_constraints:
        op.drop_constraint(
            "uq_price_table_pn_destination", "price_table", type_="unique"
        )

    indexes = {idx["name"]: idx for idx in inspector.get_indexes("price_table")}
    ix_pn = indexes.get("ix_price_table_pn")
    if ix_pn:
        op.drop_index("ix_price_table_pn", table_name="price_table")

    op.create_index("ix_price_table_pn", "price_table", ["pn"], unique=True)
