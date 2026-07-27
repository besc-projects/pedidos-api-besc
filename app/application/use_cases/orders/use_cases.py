from __future__ import annotations

from typing import Optional

from app.domain.entities.order import Order
from app.domain.entities.product import Product
from app.domain.exceptions import NotFoundException, ValidationException
from app.domain.protocols.order_repository import OrderRepositoryProtocol
from app.schemas.orders import OrderCreate, OrderUpdate

NEW_ORDER_PROCESS_ID = 1
NEW_ORDER_STATUS_CODE = 0


class CreateOrderUseCase:
    """Create an order with the default process and status."""

    def __init__(self, repository: OrderRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: OrderCreate) -> Order:
        payload = data.model_dump(exclude={"products"})
        order = Order(**payload)
        order.process_id = NEW_ORDER_PROCESS_ID
        order.status_code = NEW_ORDER_STATUS_CODE
        return await self._repository.create(order)


class GetOrderWithProductsUseCase:
    """Retrieve an order and its products by its Vale order id."""

    def __init__(self, repository: OrderRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, vale_order_id: int) -> tuple[Order, list[Product]]:
        found = await self._repository.get_with_products(vale_order_id)
        if found is None:
            raise NotFoundException("Order not found.")
        return found


class ListPendingOrdersUseCase:
    """List orders in the pending process/status."""

    def __init__(self, repository: OrderRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, skip: int, limit: int
    ) -> list[tuple[Order, list[Product]]]:
        orders = await self._repository.list_by_process_status(
            NEW_ORDER_PROCESS_ID, NEW_ORDER_STATUS_CODE, skip, limit
        )
        if not orders:
            raise NotFoundException("No orders found.")
        return orders


class ListOrdersByStatusUseCase:
    """List orders filtered by process and status."""

    def __init__(self, repository: OrderRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, process_id: int, status_code: int, skip: int, limit: int
    ) -> list[tuple[Order, list[Product]]]:
        orders = await self._repository.list_by_process_status(
            process_id, status_code, skip, limit
        )
        if not orders:
            raise NotFoundException(
                f"No orders found for process_id={process_id} "
                f"and status_code={status_code}."
            )
        return orders


class ListOrdersWithTaxReferenceUseCase:
    """List orders and their products' tax references for a reporting view."""

    def __init__(self, repository: OrderRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, vale_order_id: Optional[int], skip: int, limit: int
    ) -> list[dict]:
        orders = await self._repository.list_with_tax_reference(
            vale_order_id, skip, limit
        )
        if not orders:
            message = "No orders found for process_id=2, status_code=1"
            if vale_order_id is not None:
                message += f", vale_order_id={vale_order_id}"
            raise NotFoundException(message + ".")
        return orders


class UpdateOrderStatusUseCase:
    """Update the process and status of an order."""

    def __init__(self, repository: OrderRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, vale_order_id: int, process_id: int, status_code: int
    ) -> Order:
        order = await self._repository.set_status_by_vale(
            vale_order_id, process_id, status_code
        )
        if order is None:
            raise NotFoundException("Order not found.")
        return order


class UpdateOrderUseCase:
    """Apply a partial update to an order by its Vale order id."""

    def __init__(self, repository: OrderRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, vale_order_id: int, data: OrderUpdate
    ) -> tuple[list[str], Order]:
        changes = data.model_dump(exclude_unset=True)
        if not changes:
            raise ValidationException("No fields to update.")

        order = await self._repository.update_by_vale(vale_order_id, changes)
        if order is None:
            raise NotFoundException("Order not found.")
        return list(changes.keys()), order


class DeleteOrderUseCase:
    """Delete an order and its products by internal id."""

    def __init__(self, repository: OrderRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, order_id: int) -> None:
        deleted = await self._repository.delete_by_id(order_id)
        if not deleted:
            raise NotFoundException("Order not found.")
