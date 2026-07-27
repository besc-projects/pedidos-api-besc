from sqlalchemy import BigInteger, Column, ForeignKey, String, UniqueConstraint

from app.db.base import Base


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("order_id", name="uq_invoice_order"),
        {"schema": "billing"},
    )

    order_id = Column(
        BigInteger,
        ForeignKey("core.orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    supra_id = Column(BigInteger, nullable=False)
    issue_code = Column(String(100), nullable=False)
    transmission_code = Column(String(100), nullable=True)
