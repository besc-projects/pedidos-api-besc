from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TicketDivergence:
    """Domain representation of a ticket divergence."""

    ticket_id: int
    item_id: int
    purchase_order_line: int
    legal_basis: Optional[str] = None
    taxes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
