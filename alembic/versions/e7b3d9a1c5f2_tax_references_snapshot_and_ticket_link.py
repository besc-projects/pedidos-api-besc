"""tax_references: snapshot do valor declarado e vínculo com o chamado

Guarda, na detecção da divergência, o valor declarado (o "antes") ao lado da
referência do SUPRA (o "certo"), e liga a linha ao chamado que a trata. Sem
isso, o declarado só existe ao vivo em core.products e some quando o Coupa
atualiza o pedido. Todas as colunas são opcionais: quem já lê/escreve a tabela
(besc-ticket-management, besc-commercial-report) segue funcionando igual.

Revision ID: e7b3d9a1c5f2
Revises: d1f3a5b7c9e2
"""
from alembic import op
import sqlalchemy as sa

revision = "e7b3d9a1c5f2"
down_revision = "d1f3a5b7c9e2"
branch_labels = None
depends_on = None

_SCHEMA = "pricing"
_TABLE = "tax_references"


def upgrade() -> None:
    op.add_column(_TABLE, sa.Column("declared_ncm_code", sa.String(10), nullable=True), schema=_SCHEMA)
    op.add_column(_TABLE, sa.Column("declared_ipi", sa.Numeric(5, 2), nullable=True), schema=_SCHEMA)
    op.add_column(_TABLE, sa.Column("declared_icms", sa.Numeric(5, 2), nullable=True), schema=_SCHEMA)
    op.add_column(_TABLE, sa.Column("declared_icms_st", sa.Numeric(5, 2), nullable=True), schema=_SCHEMA)
    op.add_column(_TABLE, sa.Column("declared_origin", sa.String(50), nullable=True), schema=_SCHEMA)
    op.add_column(_TABLE, sa.Column("ticket_id", sa.Integer(), nullable=True), schema=_SCHEMA)
    op.add_column(_TABLE, sa.Column("resolved_at", sa.DateTime(), nullable=True), schema=_SCHEMA)
    op.create_index(
        "ix_tax_references_ticket_id", _TABLE, ["ticket_id"], schema=_SCHEMA
    )


def downgrade() -> None:
    op.drop_index("ix_tax_references_ticket_id", table_name=_TABLE, schema=_SCHEMA)
    for column in (
        "resolved_at",
        "ticket_id",
        "declared_origin",
        "declared_icms_st",
        "declared_icms",
        "declared_ipi",
        "declared_ncm_code",
    ):
        op.drop_column(_TABLE, column, schema=_SCHEMA)
