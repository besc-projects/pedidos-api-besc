from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class HistoryProcessEntry:
    """Domain representation of a process-history event."""

    order_id: int
    step: str
    description: str
    severity: str = "info"
    created_by: Optional[str] = None
    occurred_at: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
