from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TicketBase(BaseModel):
    order_id: Optional[int] = None
    ticket_number: Optional[int] = None
    purchase_order: Optional[int] = None
    opened_at: Optional[date] = None
    closed_at: Optional[date] = None
    observer_range_date: Optional[str] = None
    status_id: int = 0
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    order_id: Optional[int] = None
    ticket_number: Optional[int] = None
    purchase_order: Optional[int] = None
    opened_at: Optional[date] = None
    closed_at: Optional[date] = None
    observer_range_date: Optional[str] = None
    status_id: Optional[int] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TicketResponse(TicketBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TicketUpdateResponse(BaseModel):
    message: str
    updated_fields: list[str]
    ticket: TicketResponse

    model_config = ConfigDict(from_attributes=True)
