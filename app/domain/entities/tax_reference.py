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
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
