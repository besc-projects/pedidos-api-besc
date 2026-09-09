from sqlalchemy import Column, String, UniqueConstraint

from app.db.base import Base


class FiscalNotification(Base):
    """Um produto já avisado por falta de cadastro fiscal (`sgr_cadastro_produto_fiscal`
    no SUPRA) — controle de "já mandei esse e-mail 1x" que antes vivia num JSON
    local no `besc-commercial-pre-orders` (`data/fiscal_notified.json`).

    `id`/`created_at`/`updated_at` vêm de `Base`; `created_at` já é o momento do
    aviso — não precisa de coluna própria pra isso.
    """

    __tablename__ = "fiscal_notifications"
    __table_args__ = (
        UniqueConstraint("part_number", name="uq_fiscal_notifications_part_number"),
        {"schema": "fiscal"},
    )

    part_number = Column(String(100), nullable=False, index=True)
