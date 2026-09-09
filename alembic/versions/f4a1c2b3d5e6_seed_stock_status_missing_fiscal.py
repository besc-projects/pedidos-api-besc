"""seed stock_status id 5 (missing fiscal registration)

Revision ID: f4a1c2b3d5e6
Revises: c4e6a8b0d2f4
Create Date: 2026-09-08 00:00:00.000000

core.stock_status nunca foi criada por uma migration deste repo (não há
modelo ORM nem migration anterior que a referencie) — só existe hoje como um
LEFT JOIN cru em GET /api/dashboard/inventory/by-status. Sem uma linha para o
id, o dashboard mostra "status 5" em vez de um nome (coalesce(ss.name,
CONCAT('status ', p.stock_status_id))), mas a query não quebra — daí dar pra
fazer isso como seed em vez de precisar criar a tabela.

Não mexe nos ids já em uso (0 = normal, 4 = divergência de preço): produção
já tem nomes reais para eles (confirmado via /inventory/by-status) e não sei
quais são — só insere o 5, que é novo (confirmado: a linha não existe ainda).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4a1c2b3d5e6"
down_revision: Union[str, Sequence[str], None] = "c4e6a8b0d2f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("stock_status", schema="core"):
        return

    columns = {column["name"] for column in inspector.get_columns("stock_status", schema="core")}
    if "id" not in columns or "name" not in columns:
        return

    # `description` é NOT NULL sem default (confirmado via INFORMATION_SCHEMA) —
    # `created_at`/`updated_at` têm default (sysutcdatetime()), não precisam entrar aqui.
    # IF NOT EXISTS em vez de ON CONFLICT: produção é SQL Server, não Postgres.
    # id é IDENTITY -> precisa de IDENTITY_INSERT ON pra permitir o valor explícito.
    op.execute(
        sa.text(
            """
            IF NOT EXISTS (SELECT 1 FROM core.stock_status WHERE id = 5)
            BEGIN
                SET IDENTITY_INSERT core.stock_status ON
                INSERT INTO core.stock_status (id, name, description)
                VALUES (5, 'Sem Cadastro Fiscal', 'Produto sem linha em dbo.sgr_cadastro_produto_fiscal no SUPRA — pré-pedido bloqueado até o Fiscal cadastrar')
                SET IDENTITY_INSERT core.stock_status OFF
            END
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("stock_status", schema="core"):
        return

    op.execute(sa.text("DELETE FROM core.stock_status WHERE id = 5"))
