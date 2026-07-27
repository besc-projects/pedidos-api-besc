from typing import Optional, Protocol

from app.domain.entities.price_table_entry import PriceTableEntry


class PriceTableRepositoryProtocol(Protocol):
    """Persistence contract for price-table entries."""

    async def get_by_id(self, entry_id: int) -> Optional[PriceTableEntry]:
        ...

    async def get_by_pn_and_destination(
        self, pn: str, destination: str
    ) -> Optional[PriceTableEntry]:
        ...

    async def list(self, skip: int, limit: int) -> list[PriceTableEntry]:
        ...

    async def create(self, entry: PriceTableEntry) -> PriceTableEntry:
        ...

    async def update(self, entry: PriceTableEntry, changes: dict) -> PriceTableEntry:
        ...

    async def delete(self, entry_id: int) -> bool:
        ...
