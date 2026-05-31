from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class TicketProgress(Base):
    __tablename__ = "ticket_progresses"
    __table_args__ = {"schema": "support"}

    ticket_id = Column(
        Integer,
        ForeignKey(
            "support.tickets.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    status_progress_id = Column(Integer, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    ticket = relationship("Ticket", back_populates="progresses")
