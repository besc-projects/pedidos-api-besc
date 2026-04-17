from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    order_id = Column(
        Integer,
        ForeignKey("orders.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )

    item = Column(String(10))
    part_number = Column(String(50))
    description = Column(Text)
    ncm_code = Column(String(20))
    unit = Column(String(10))
    quantity = Column(Integer, default=0)
    unit_price = Column(Numeric(12, 2), default=0)
    material = Column(String(255))
    origin = Column(String(255))
    payment_date = Column(TIMESTAMP, nullable=True)
    billing_until = Column(TIMESTAMP, nullable=True)
    stock_status_id = Column(Integer, default=0)
    icms = Column(Numeric(5, 2), default=0)
    icms_st = Column(Numeric(5, 2), default=0)
    ipi = Column(Numeric(5, 2), default=0)
    tickets_status_id = Column(Integer, default=None)
    # Relationships
    order = relationship(
        "Order",
        back_populates="products",
        foreign_keys=[order_id],
    )
