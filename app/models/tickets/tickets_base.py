from sqlalchemy import (
    Column,
    Integer,
    Date,
    Text,
    ForeignKey,
    String,
    BigInteger,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": "support"}

    order_id = Column(
        Integer,
        ForeignKey("core.orders.id"),
        nullable=True,
    )

    ticket_number = Column(Integer, unique=True, nullable=True)
    purchase_order = Column(BigInteger, unique=True, nullable=True)

    opened_at = Column(Date, nullable=True)
    closed_at = Column(Date, nullable=True)

    observer_range_date = Column(String(30), nullable=True)

    status_id = Column(
        Integer,
        ForeignKey("support.tickets_status.id"),
    )

    notes = Column(Text)

    order = relationship(
        "Order",
        back_populates="tickets"
    )

    status = relationship(
        "TicketStatus",
        back_populates="tickets"
    )

    progresses = relationship(
        "TicketProgress",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    divergences = relationship(
        "TicketDivergence",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )