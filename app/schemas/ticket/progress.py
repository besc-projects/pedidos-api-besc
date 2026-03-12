from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TicketProgressBase(BaseModel):
    status_progress_id: int = Field(..., ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TicketProgressCreate(TicketProgressBase):
    pass


class TicketProgressUpdate(BaseModel):
    status_progress_id: Optional[int] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TicketProgressResponse(TicketProgressBase):
    id: int
    ticket_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
