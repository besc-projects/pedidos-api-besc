from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from app.application.use_cases.orders.use_cases import (
    CreateOrderUseCase,
    DeleteOrderUseCase,
    GetOrderWithProductsUseCase,
    ListPendingOrdersUseCase,
    UpdateOrderStatusUseCase,
    UpdateOrderUseCase,
)
from app.domain.entities.order import Order
from app.domain.entities.product import Product
from app.domain.exceptions import NotFoundException, ValidationException
from app.schemas.orders import OrderCreate, OrderUpdate


class FakeOrderRepository:
    def __init__(self) -> None:
        self._items: list[Order] = []
        self._next_id = 1

    async def create(self, order: Order) -> Order:
        order.id = self._next_id
        self._next_id += 1
        self._items.append(order)
        return order

    async def get_with_products(
        self, vale_order_id: int
    ) -> Optional[tuple[Order, list[Product]]]:
        order = next(
            (o for o in self._items if o.vale_order_id == vale_order_id), None
        )
        return (order, []) if order else None

    async def list_by_process_status(self, process_id, status_code, skip, limit):
        return [
            (o, [])
            for o in self._items
            if o.process_id == process_id and o.status_code == status_code
        ][skip : skip + limit]

    async def list_with_tax_reference(self, vale_order_id, skip, limit):
        return []

    async def update_by_vale(self, vale_order_id, changes) -> Optional[Order]:
        order = next(
            (o for o in self._items if o.vale_order_id == vale_order_id), None
        )
        if order is None:
            return None
        for field, value in changes.items():
            setattr(order, field, value)
        return order

    async def set_status_by_vale(self, vale_order_id, process_id, status_code):
        order = next(
            (o for o in self._items if o.vale_order_id == vale_order_id), None
        )
        if order is None:
            return None
        order.process_id = process_id
        order.status_code = status_code
        return order

    async def delete_by_id(self, order_id: int) -> bool:
        order = next((o for o in self._items if o.id == order_id), None)
        if order is None:
            return False
        self._items.remove(order)
        return True


def _payload(**overrides) -> OrderCreate:
    data = {
        "vale_order_id": 5000,
        "total_value": 100.0,
        "cnpj": "00000000000000",
        "portal": "p",
        "center": "c",
        "state": "MG",
        "date": datetime(2026, 1, 1),
    }
    data.update(overrides)
    return OrderCreate.model_validate(data)


async def test_create_order_sets_defaults():
    repository = FakeOrderRepository()
    order = await CreateOrderUseCase(repository).execute(_payload())
    assert order.process_id == 1
    assert order.status_code == 0


async def test_list_pending_orders():
    repository = FakeOrderRepository()
    await CreateOrderUseCase(repository).execute(_payload())
    orders = await ListPendingOrdersUseCase(repository).execute(0, 10)
    assert len(orders) == 1


async def test_list_pending_orders_empty():
    with pytest.raises(NotFoundException):
        await ListPendingOrdersUseCase(FakeOrderRepository()).execute(0, 10)


async def test_get_order_not_found():
    with pytest.raises(NotFoundException):
        await GetOrderWithProductsUseCase(FakeOrderRepository()).execute(1)


async def test_update_order_no_fields():
    repository = FakeOrderRepository()
    await CreateOrderUseCase(repository).execute(_payload())
    with pytest.raises(ValidationException):
        await UpdateOrderUseCase(repository).execute(5000, OrderUpdate())


async def test_update_order_status_not_found():
    with pytest.raises(NotFoundException):
        await UpdateOrderStatusUseCase(FakeOrderRepository()).execute(9, 2, 1)


async def test_delete_order_not_found():
    with pytest.raises(NotFoundException):
        await DeleteOrderUseCase(FakeOrderRepository()).execute(1)
