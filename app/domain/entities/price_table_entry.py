from dataclasses import dataclass
from typing import Optional


@dataclass
class PriceTableEntry:
    """Domain representation of a price-table entry."""

    pn: str
    long_description: str
    description: str
    destination: str
    unit_price: float
    id: Optional[int] = None

    def __post_init__(self) -> None:
        self.destination = self.normalize_destination(self.destination)

    @staticmethod
    def normalize_destination(destination: str) -> str:
        """Destinations are compared case-insensitively and trimmed."""
        return destination.strip().upper()
