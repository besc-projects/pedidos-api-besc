from app.models.status.base import BaseStatus

from sqlalchemy.orm import relationship


class ProposalsStatus(BaseStatus):
    __tablename__ = "proposals_status"
    __table_args__ = {"schema": "commercial"}

    proposals = relationship(
        "Proposal",
        back_populates="proposals_status"
    )