from sqlalchemy import Column, DateTime, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Proposal(Base):
    __tablename__ = "proposals"
    __table_args__ = {"schema": "commercial"}

    proposal_number = Column(Integer, unique=True)

    status_id = Column(
        Integer,
        ForeignKey(
            "commercial.proposals_status.id",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
    )

    email = Column(String(255), nullable=True)
    request_date = Column(DateTime, nullable=True)

    proposals_status = relationship(
        "ProposalsStatus",
        back_populates="proposals"
    )

    order = relationship(
        "Order",
        back_populates="proposals",
        cascade="all, delete-orphan"
    )