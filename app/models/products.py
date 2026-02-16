from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    order_id = Column(
        Integer,
        ForeignKey("orders.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    tax_id = Column(
        Integer, ForeignKey("tax.id", onupdate="CASCADE", ondelete="SET NULL")
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

    # Relationships
    order = relationship(
        "Order",
        back_populates="products",
        foreign_keys=[order_id],
    )
    tax = relationship("Tax", back_populates="products")
