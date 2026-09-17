"""unique index for process_history dedup (order_id, description)

Revision ID: d1f3a5b7c9e2
Revises: c8a2e6f4b1d3
Create Date: 2026-09-17 00:00:00.000000

audit.process_history não tinha nenhum índice além do PK. A checagem de
duplicata (order_id, description) fazia table scan a cada escrita, e como a
checagem é check-then-insert (não atômica), sob concorrência (vários robôs
escrevendo ao mesmo tempo) isso tendia a escalar pra lock de tabela — achado
de 17/09/2026, depois que o rastreio (audit.process_history) foi ligado em
mais robôs e o volume de escrita cresceu.

description era VARCHAR(MAX) (sem tamanho), que o SQL Server não deixa
indexar direto — reduzido para VARCHAR(400) (maior valor real hoje: 80
caracteres, então há folga de sobra) pra caber no limite de 900 bytes de
chave de índice.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d1f3a5b7c9e2"
down_revision: Union[str, Sequence[str], None] = "c8a2e6f4b1d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_INDEX_NAME = "uq_audit_process_history_order_description"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("process_history", schema="audit"):
        return

    columns = {c["name"]: c for c in inspector.get_columns("process_history", schema="audit")}
    description_col = columns.get("description")
    if description_col is not None and getattr(description_col["type"], "length", "unset") != 400:
        op.alter_column(
            "process_history", "description",
            existing_type=sa.Text(), type_=sa.String(400),
            existing_nullable=False, schema="audit",
        )

    indexes = {index["name"] for index in inspector.get_indexes("process_history", schema="audit")}
    if _INDEX_NAME not in indexes:
        op.create_index(
            _INDEX_NAME, "process_history", ["order_id", "description"],
            unique=True, schema="audit",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("process_history", schema="audit"):
        return

    indexes = {index["name"] for index in inspector.get_indexes("process_history", schema="audit")}
    if _INDEX_NAME in indexes:
        op.drop_index(_INDEX_NAME, table_name="process_history", schema="audit")

    columns = {c["name"] for c in inspector.get_columns("process_history", schema="audit")}
    if "description" in columns:
        op.alter_column(
            "process_history", "description",
            existing_type=sa.String(400), type_=sa.Text(),
            existing_nullable=False, schema="audit",
        )
