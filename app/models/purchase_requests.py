from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Numeric,
    Enum as SAEnum,
    UniqueConstraint,
)
from app.db.base import Base
from app.domain.enums.purchase_request_status import PurchaseRequestStatus


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"
    __table_args__ = (
        UniqueConstraint("order_id", "part_number", name="uq_order_part_number"),
        {"schema": "purchasing"},
    )

    order_id = Column(BigInteger, nullable=False, index=True)
    product_id = Column(BigInteger, nullable=False)
    supplier_product_code = Column(String(100), nullable=True)
    part_number = Column(String(100), nullable=False, index=True)
    released_quantity = Column(Numeric(12, 2), nullable=False)
    requested_quantity = Column(Numeric(12, 2), nullable=False)
    status = Column(
        SAEnum(PurchaseRequestStatus, name="purchase_request_status", schema="purchasing"),
        default=PurchaseRequestStatus.PENDING,
        nullable=False,
    )
