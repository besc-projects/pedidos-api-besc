from sqlalchemy import BigInteger, Column, String, UniqueConstraint

from app.db.base import Base


class FiscalNotification(Base):
    """Um produto já avisado por falta de cadastro fiscal (`sgr_cadastro_produto_fiscal`
    no SUPRA) — controle de "já mandei esse e-mail 1x" (hoje usado pelo
    `cadastro-fiscal` do besc-commercial-report).

    `id`/`created_at`/`updated_at` vêm de `Base`; `created_at` já é o momento do
    aviso — não precisa de coluna própria pra isso.
    """

    __tablename__ = "fiscal_notifications"
    __table_args__ = (
        UniqueConstraint("part_number", name="uq_fiscal_notifications_part_number"),
        {"schema": "fiscal"},
    )

    part_number = Column(String(100), nullable=False, index=True)
    # Pedido que disparou o aviso — dedup é por produto (mesmo PN pode
    # bloquear vários pedidos), mas sem isso a linha era inauditável: não dava
    # pra saber por causa de qual pedido o aviso saiu. Nullable: linhas criadas
    # antes desta coluna existir (ver migration 5794aafc976d) não têm esse dado.
    vale_order_id = Column(BigInteger, nullable=True)
