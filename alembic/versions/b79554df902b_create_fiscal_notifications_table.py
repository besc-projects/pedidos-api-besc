"""create fiscal.fiscal_notifications table

Revision ID: b79554df902b
Revises: f4a1c2b3d5e6
Create Date: 2026-09-09 00:00:00.000000

Controle de "produto X já foi avisado por falta de cadastro fiscal
(dbo.sgr_cadastro_produto_fiscal no SUPRA)" — antes vivia num JSON local no
besc-commercial-pre-orders (data/fiscal_notified.json), passa a ser uma
tabela na API pra não depender de disco local de um robô específico.

Usa op.create_table (não SQL cru) pra a DDL sair correta pro dialeto real da
conexão (produção é SQL Server, não Postgres — ver f4a1c2b3d5e6 pra contexto).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b79554df902b"
down_revision: Union[str, Sequence[str], None] = "f4a1c2b3d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "fiscal"
TABLE = "fiscal_notifications"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if SCHEMA not in inspector.get_schema_names():
        op.execute(sa.text(f"CREATE SCHEMA {SCHEMA}"))

    if not inspector.has_table(TABLE, schema=SCHEMA):
        op.create_table(
            TABLE,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("part_number", sa.String(length=100), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "part_number", name="uq_fiscal_notifications_part_number"
            ),
            schema=SCHEMA,
        )
        op.create_index(
            "ix_fiscal_notifications_part_number",
            TABLE,
            ["part_number"],
            schema=SCHEMA,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table(TABLE, schema=SCHEMA):
        op.drop_table(TABLE, schema=SCHEMA)
