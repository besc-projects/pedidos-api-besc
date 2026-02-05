"""initial_tables

Revision ID: e780a412346d
Revises: 70a5e15f5b84
Create Date: 2026-02-05 15:23:15.199935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e780a412346d'
down_revision: Union[str, Sequence[str], None] = '70a5e15f5b84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
