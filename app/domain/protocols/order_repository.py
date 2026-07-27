from __future__ import annotations

from typing import Optional, Protocol

from app.domain.entities.order import Order
from app.domain.entities.product import Product


class OrderRepositoryProtocol(Protocol):
    """Persistence contract for purchase orders."""

    async def create(self, order: Order) -> Order:
        ...

    async def get_with_products(
        self, vale_order_id: int
    ) -> Optional[tuple[Order, list[Product]]]:
        ...

    async def list_by_process_status(
        self, process_id: int, status_code: int, skip: int, limit: int
    ) -> list[tuple[Order, list[Product]]]:
        ...

    async def list_with_tax_reference(
        self, vale_order_id: Optional[int], skip: int, limit: int
    ) -> list[dict]:
        ...

    async def update_by_vale(
        self, vale_order_id: int, changes: dict
    ) -> Optional[Order]:
        ...

    async def set_status_by_vale(
        self, vale_order_id: int, process_id: int, status_code: int
    ) -> Optional[Order]:
        ...

    async def delete_by_id(self, order_id: int) -> bool:
        ...
