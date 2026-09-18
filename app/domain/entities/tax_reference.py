from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class TaxReference:
    """Domain representation of a product tax reference (Supra)."""

    id_product: int
    ncm_code: str
    ipi: Optional[Decimal] = None
    icms: Optional[Decimal] = None
    icms_st: Optional[Decimal] = None
    origin: Optional[str] = None
    declared_ncm_code: Optional[str] = None
    declared_ipi: Optional[Decimal] = None
    declared_icms: Optional[Decimal] = None
    declared_icms_st: Optional[Decimal] = None
    declared_origin: Optional[str] = None
    ticket_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
