from __future__ import annotations

from typing import Optional, Protocol

from app.domain.entities.product import Product


class ProductRepositoryProtocol(Protocol):
    """Persistence contract for order products."""

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        ...

    async def list_by_order(self, order_id: int) -> list[Product]:
        ...

    async def get_internal_order_id(self, vale_order_id: int) -> Optional[int]:
        ...

    async def find_in_order_by_part_number(
        self, order_id: int, part_number: str
    ) -> Optional[Product]:
        ...

    async def find_in_order_by_item(
        self, order_id: int, item: str
    ) -> Optional[Product]:
        ...

    async def create(self, product: Product) -> Product:
        ...

    async def update(self, product_id: int, changes: dict) -> Product:
        ...
