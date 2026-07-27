from __future__ import annotations

from typing import Optional

import pytest

from app.application.use_cases.products.use_cases import (
    CreateProductUseCase,
    GetProductUseCase,
    UpdateProductUseCase,
)
from app.domain.entities.product import Product
from app.domain.exceptions import NotFoundException
from app.schemas.products import ProductCreate, ProductUpdate


class FakeProductRepository:
    def __init__(self, internal_order_id: Optional[int] = 1) -> None:
        self._items: list[Product] = []
        self._next_id = 1
        self._internal_order_id = internal_order_id

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        return next((p for p in self._items if p.id == product_id), None)

    async def list_by_order(self, order_id: int) -> list[Product]:
        return [p for p in self._items if p.order_id == order_id]

    async def get_internal_order_id(self, vale_order_id: int) -> Optional[int]:
        return self._internal_order_id

    async def find_in_order_by_part_number(
        self, order_id: int, part_number: str
    ) -> Optional[Product]:
        return next(
            (
                p
                for p in self._items
                if p.order_id == order_id and p.part_number == part_number
            ),
            None,
        )

    async def find_in_order_by_item(
        self, order_id: int, item: str
    ) -> Optional[Product]:
        return next(
            (p for p in self._items if p.order_id == order_id and p.item == item),
            None,
        )

    async def create(self, product: Product) -> Product:
        product.id = self._next_id
        self._next_id += 1
        self._items.append(product)
        return product

    async def update(self, product_id: int, changes: dict) -> Product:
        product = next(p for p in self._items if p.id == product_id)
        for field, value in changes.items():
            setattr(product, field, value)
        return product


async def test_create_new_product():
    repository = FakeProductRepository(internal_order_id=7)
    product = await CreateProductUseCase(repository).execute(
        ProductCreate(order_id=1001, part_number="PN1", description="a")
    )
    assert product.id == 1
    assert product.order_id == 7


async def test_create_upserts_existing_part_number():
    repository = FakeProductRepository(internal_order_id=7)
    use_case = CreateProductUseCase(repository)
    await use_case.execute(ProductCreate(order_id=1001, part_number="PN1", description="a"))
    updated = await use_case.execute(
        ProductCreate(order_id=1001, part_number="PN1", description="b")
    )
    assert updated.id == 1
    assert updated.description == "b"
    assert len(repository._items) == 1


async def test_create_order_not_found():
    repository = FakeProductRepository(internal_order_id=None)
    with pytest.raises(NotFoundException):
        await CreateProductUseCase(repository).execute(
            ProductCreate(order_id=9999, part_number="PN1")
        )


async def test_get_product_not_found():
    with pytest.raises(NotFoundException):
        await GetProductUseCase(FakeProductRepository()).execute(1)


async def test_update_product_not_found():
    with pytest.raises(NotFoundException):
        await UpdateProductUseCase(FakeProductRepository()).execute(
            1, ProductUpdate(description="x")
        )
