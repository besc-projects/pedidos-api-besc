"""add vale_order_id to fiscal.fiscal_notifications

Revision ID: 5794aafc976d
Revises: b79554df902b
Create Date: 2026-09-09 00:00:00.000000

O dedup é por `part_number` de propósito (mesmo PN bloqueia vários pedidos,
um só aviso por produto) — mas sem nenhuma referência de pedido a tabela era
inauditável: olhando uma linha não dava pra saber "esse aviso saiu por causa
de qual pedido?". Guarda o `vale_order_id` do pedido que disparou o aviso
(o primeiro a encontrar o produto bloqueado — como o dedup impede reaviso, só
existe essa uma ocorrência mesmo). Nullable: a linha já existente (EF04862,
criada antes desta coluna existir) fica sem essa informação — não dá pra
reconstruir retroativamente, então backfill manual pra esse caso específico
(vale_order_id=4513535908, confirmado pelo contexto da conversa que criou
essa linha).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5794aafc976d"
down_revision: Union[str, Sequence[str], None] = "b79554df902b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "fiscal"
TABLE = "fiscal_notifications"
COLUMN = "vale_order_id"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table(TABLE, schema=SCHEMA):
        return

    columns = {c["name"] for c in inspector.get_columns(TABLE, schema=SCHEMA)}
    if COLUMN in columns:
        return

    op.add_column(TABLE, sa.Column(COLUMN, sa.BigInteger(), nullable=True), schema=SCHEMA)

    # Backfill da única linha que já existia antes desta coluna existir.
    op.execute(
        sa.text(
            f"UPDATE {SCHEMA}.{TABLE} SET {COLUMN} = 4513535908 "
            "WHERE part_number = 'EF04862' AND vale_order_id IS NULL"
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table(TABLE, schema=SCHEMA):
        return

    columns = {c["name"] for c in inspector.get_columns(TABLE, schema=SCHEMA)}
    if COLUMN not in columns:
        return

    op.drop_column(TABLE, COLUMN, schema=SCHEMA)
