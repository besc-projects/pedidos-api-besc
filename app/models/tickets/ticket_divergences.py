from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class TicketDivergence(Base):
    __tablename__ = "ticket_divergences"
    __table_args__ = {"schema": "support"}


    item_id = Column(Integer, nullable=True)
    ticket_id = Column(
        Integer,
        ForeignKey("support.tickets.id", 
            onupdate="CASCADE", 
            ondelete="CASCADE"),
        nullable=False,
    )
    legal_basis = Column(Text, nullable=True)
    purchase_order_line = Column(Integer, nullable=True)
    taxes = Column(Text, nullable=True)

    ticket = relationship("Ticket", back_populates="divergences")

