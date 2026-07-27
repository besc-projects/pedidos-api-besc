from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Optional

CONCLUDED_STATUS_ID = 2


@dataclass
class Ticket:
    """Domain representation of a support ticket."""

    order_id: Optional[int] = None
    ticket_number: Optional[int] = None
    purchase_order: Optional[int] = None
    opened_at: Optional[date] = None
    closed_at: Optional[date] = None
    observer_range_date: Optional[str] = None
    status_id: int = 0
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_concluded(self) -> bool:
        """Status 2 represents the concluded state in the ticket workflow."""
        return self.status_id == CONCLUDED_STATUS_ID

    @staticmethod
    def today_iso() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
