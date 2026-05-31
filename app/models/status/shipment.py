from app.models.status.base import BaseStatus
from sqlalchemy.orm import relationship


class ShipmentStatus(BaseStatus):
    __tablename__ = "shipments_status"
    __table_args__ = {"schema": "logistics"}

    shipments = relationship(
        "Shipment",
        back_populates="shipments_status"
    )