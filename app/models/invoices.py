from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.db.base import Base


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("order_id", name="uq_invoice_order"),
        {"schema": "billing"},
    )

    order_id = Column(
        Integer,
        ForeignKey("core.orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_emissao = Column(Integer, nullable=False)
    id_transmissao = Column(Integer, nullable=True)
    nfe = Column(String(100), nullable=True)
    data = Column(DateTime(timezone=True), nullable=False)
