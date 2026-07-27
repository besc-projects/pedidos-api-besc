from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Order:
    """Domain representation of a purchase order."""

    vale_order_id: int
    total_value: float
    cnpj: str
    date: datetime
    process_id: int = 0
    status_code: int = 0
    state: Optional[str] = None
    ticket_id: Optional[int] = None
    portal: Optional[str] = None
    center: Optional[str] = None
    besc_order_id: Optional[int] = None
    contract_number: Optional[str] = None
    invoice_number: Optional[str] = None
    days_to_delivery: Optional[str] = None
    version: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
