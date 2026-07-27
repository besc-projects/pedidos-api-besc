from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """Domain representation of an order product line."""

    order_id: Optional[int] = None
    item: Optional[str] = None
    part_number: Optional[str] = None
    description: Optional[str] = None
    ncm_code: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    quantity: Optional[int] = None
    material: Optional[str] = None
    origin: Optional[str] = None
    payment_date: Optional[datetime] = None
    billing_until: Optional[datetime] = None
    ipi: Optional[float] = None
    icms: Optional[float] = None
    icms_st: Optional[float] = None
    tickets_status_id: Optional[int] = None
    stock_status_id: Optional[int] = 0
    id: Optional[int] = None
