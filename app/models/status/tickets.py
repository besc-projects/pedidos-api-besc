from app.models.status.base import BaseStatus
from sqlalchemy.orm import relationship


class TicketStatus(BaseStatus):
    __tablename__ = "tickets_status"
    __table_args__ = {"schema": "support"}

    tickets = relationship(
        "Ticket",
        back_populates="status"
    )