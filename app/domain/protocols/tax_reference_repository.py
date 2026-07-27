from __future__ import annotations

from typing import Optional, Protocol

from app.domain.entities.tax_reference import TaxReference


class TaxReferenceRepositoryProtocol(Protocol):
    """Persistence contract for product tax references."""

    async def get_by_id(self, entry_id: int) -> Optional[TaxReference]:
        ...

    async def list_by_product(self, id_product: int) -> list[TaxReference]:
        ...

    async def list_by_order(self, vale_order_id: int) -> list[TaxReference]:
        ...

    async def list(self, skip: int, limit: int) -> list[TaxReference]:
        ...

    async def create(self, tax_reference: TaxReference) -> TaxReference:
        ...

    async def update(self, tax_reference: TaxReference, changes: dict) -> TaxReference:
        ...

    async def delete(self, entry_id: int) -> bool:
        ...
