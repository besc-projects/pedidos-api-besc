from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProposalBase(BaseModel):
    proposal_number: Optional[int] = None
    status_id: Optional[int] = None
    email: Optional[str] = None
    request_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProposalCreate(ProposalBase):
    pass


class ProposalUpdate(ProposalBase):
    pass


class Proposal(ProposalBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    email: Optional[str] = None
    request_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
