from __future__ import annotations

from app.domain.entities.product import Product
from app.domain.exceptions import NotFoundException
from app.domain.protocols.product_repository import ProductRepositoryProtocol
from app.schemas.products import ProductCreate, ProductUpdate


class GetProductUseCase:
    """Retrieve a product by id."""

    def __init__(self, repository: ProductRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, product_id: int) -> Product:
        product = await self._repository.get_by_id(product_id)
        if product is None:
            raise NotFoundException("Product not found.")
        return product


class ListProductsByOrderUseCase:
    """List products linked to an internal order id."""

    def __init__(self, repository: ProductRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, order_id: int) -> list[Product]:
        return await self._repository.list_by_order(order_id)


class CreateProductUseCase:
    """Create or update a product line within an order (upsert).

    A product is matched inside the order by part number and then by item; when
    found, its fields are updated, otherwise a new line is created.
    """

    def __init__(self, repository: ProductRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: ProductCreate) -> Product:
        internal_order_id = await self._repository.get_internal_order_id(data.order_id)
        if internal_order_id is None:
            raise NotFoundException("Order not found.")

        existing: Product | None = None
        if data.part_number:
            existing = await self._repository.find_in_order_by_part_number(
                internal_order_id, data.part_number
            )
        if data.item:
            existing = await self._repository.find_in_order_by_item(
                internal_order_id, data.item
            )

        if existing is not None:
            changes = data.model_dump(exclude_unset=True, exclude={"order_id"})
            changes["order_id"] = internal_order_id
            return await self._repository.update(existing.id, changes)

        product = Product(**data.model_dump())
        product.order_id = internal_order_id
        return await self._repository.create(product)


class UpdateProductUseCase:
    """Apply a partial update to a product by id."""

    def __init__(self, repository: ProductRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, product_id: int, data: ProductUpdate) -> Product:
        product = await self._repository.get_by_id(product_id)
        if product is None:
            raise NotFoundException("Product not found.")

        changes = data.model_dump(exclude_unset=True)
        if "order_id" in changes:
            internal_order_id = await self._repository.get_internal_order_id(
                changes["order_id"]
            )
            if internal_order_id is None:
                raise NotFoundException("Order not found.")
            changes["order_id"] = internal_order_id

        return await self._repository.update(product_id, changes)
