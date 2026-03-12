from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TicketDivergenceBase(BaseModel):
    legal_basis: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TicketDivergenceCreate(TicketDivergenceBase):
    purchase_order_line: int = Field(..., ge=0)
    taxes: Optional[str] = None
    item_id: int = Field(..., ge=0)


class TicketDivergenceUpdate(BaseModel):
    legal_basis: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class TicketDivergenceResponse(TicketDivergenceBase):
    id: int
    item_id: int
    ticket_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    purchase_order_line: int
    model_config = ConfigDict(from_attributes=True)
