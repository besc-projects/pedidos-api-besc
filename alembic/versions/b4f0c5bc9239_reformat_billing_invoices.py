"""reformat billing.invoices: id_emissao/id_transmissao/nfe/data, drop supra_id

Revision ID: b4f0c5bc9239
Revises: 5794aafc976d
Create Date: 2026-09-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4f0c5bc9239"
down_revision: Union[str, Sequence[str], None] = "5794aafc976d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "billing"
TABLE = "invoices"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table(TABLE, schema=SCHEMA):
        return

    columns = {c["name"] for c in inspector.get_columns(TABLE, schema=SCHEMA)}

    # 1) Colunas novas, nullable a princípio — o backfill do passo 2 preenche
    #    id_emissao/data para linhas existentes antes de travar NOT NULL.
    if "id_emissao" not in columns:
        op.add_column(TABLE, sa.Column("id_emissao", sa.Integer(), nullable=True), schema=SCHEMA)
    if "id_transmissao" not in columns:
        op.add_column(TABLE, sa.Column("id_transmissao", sa.Integer(), nullable=True), schema=SCHEMA)
    if "nfe" not in columns:
        op.add_column(TABLE, sa.Column("nfe", sa.String(100), nullable=True), schema=SCHEMA)
    if "data" not in columns:
        op.add_column(TABLE, sa.Column("data", sa.DateTime(timezone=True), nullable=True), schema=SCHEMA)

    # 2) Backfill das linhas existentes: issue_code numérico vira id_emissao;
    #    created_at vira data. Só roda se as colunas antigas ainda existirem
    #    (idempotente — reexecução da migration não falha).
    if "issue_code" in columns:
        op.execute(
            f"UPDATE [{SCHEMA}].[{TABLE}] SET id_emissao = TRY_CAST(issue_code AS INT) "
            "WHERE id_emissao IS NULL"
        )
    if "created_at" in columns:
        op.execute(
            f"UPDATE [{SCHEMA}].[{TABLE}] SET data = created_at WHERE data IS NULL"
        )

    # 3) Remove as colunas antigas.
    columns = {c["name"] for c in inspector.get_columns(TABLE, schema=SCHEMA)}
    if "supra_id" in columns:
        op.drop_column(TABLE, "supra_id", schema=SCHEMA)
    if "issue_code" in columns:
        op.drop_column(TABLE, "issue_code", schema=SCHEMA)
    if "transmission_code" in columns:
        op.drop_column(TABLE, "transmission_code", schema=SCHEMA)

    # 4) Promove id_emissao e data para NOT NULL. Se sobrar alguma linha com
    #    NULL (ex: issue_code não-numérico que o TRY_CAST não converteu), o
    #    ALTER falha explicitamente em vez de silenciar — sinal para tratar
    #    manualmente antes de reexecutar.
    op.alter_column(TABLE, "id_emissao", existing_type=sa.Integer(), nullable=False, schema=SCHEMA)
    op.alter_column(TABLE, "data", existing_type=sa.DateTime(timezone=True), nullable=False, schema=SCHEMA)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table(TABLE, schema=SCHEMA):
        return

    columns = {c["name"] for c in inspector.get_columns(TABLE, schema=SCHEMA)}

    if "supra_id" not in columns:
        op.add_column(TABLE, sa.Column("supra_id", sa.BigInteger(), nullable=True), schema=SCHEMA)
    if "issue_code" not in columns:
        op.add_column(TABLE, sa.Column("issue_code", sa.String(100), nullable=True), schema=SCHEMA)
    if "transmission_code" not in columns:
        op.add_column(TABLE, sa.Column("transmission_code", sa.String(100), nullable=True), schema=SCHEMA)

    # issue_code volta populado a partir de id_emissao (mesma conversão, ao
    # contrário); supra_id e transmission_code ficam NULL (dado não existe).
    if "id_emissao" in columns:
        op.execute(
            f"UPDATE [{SCHEMA}].[{TABLE}] SET issue_code = CAST(id_emissao AS VARCHAR(100))"
        )

    columns = {c["name"] for c in inspector.get_columns(TABLE, schema=SCHEMA)}
    if "id_emissao" in columns:
        op.drop_column(TABLE, "id_emissao", schema=SCHEMA)
    if "id_transmissao" in columns:
        op.drop_column(TABLE, "id_transmissao", schema=SCHEMA)
    if "nfe" in columns:
        op.drop_column(TABLE, "nfe", schema=SCHEMA)
    if "data" in columns:
        op.drop_column(TABLE, "data", schema=SCHEMA)
