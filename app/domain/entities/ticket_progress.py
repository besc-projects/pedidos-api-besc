from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TicketProgress:
    """Domain representation of a ticket progress step."""

    ticket_id: int
    status_progress_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
