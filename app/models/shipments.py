from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Shipment(Base):
    __tablename__ = "shipments"
    __table_args__ = {"schema": "logistics"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    order_id = Column(
        Integer,
        ForeignKey(
            "core.orders.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True,
    )

    status_id = Column(
        Integer,
        ForeignKey(
            "logistics.shipments_status.id",
            onupdate="CASCADE",
            ondelete="SET NULL"
        ),
    )

    name = Column(String, nullable=False)
    tracking_number = Column(String)
    shipment_date = Column(Date)

    order = relationship("Order", back_populates="shipment", uselist=False)
    shipments_status = relationship("ShipmentStatus", back_populates="shipments")