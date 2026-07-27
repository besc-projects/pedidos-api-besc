from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.product import Product
from app.models.orders import Order as OrderModel
from app.models.products import Product as ProductModel

_ENTITY_FIELDS = (
    "order_id",
    "item",
    "part_number",
    "description",
    "ncm_code",
    "unit",
    "unit_price",
    "quantity",
    "material",
    "origin",
    "payment_date",
    "billing_until",
    "ipi",
    "icms",
    "icms_st",
    "tickets_status_id",
    "stock_status_id",
)


class SqlAlchemyProductRepository:
    """SQLAlchemy persistence for order products."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: ProductModel) -> Product:
        return Product(id=model.id, **{f: getattr(model, f) for f in _ENTITY_FIELDS})

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_order(self, order_id: int) -> list[Product]:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.order_id == order_id)
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def get_internal_order_id(self, vale_order_id: int) -> Optional[int]:
        result = await self._session.execute(
            select(OrderModel.id).where(OrderModel.vale_order_id == vale_order_id)
        )
        return result.scalar_one_or_none()

    async def find_in_order_by_part_number(
        self, order_id: int, part_number: str
    ) -> Optional[Product]:
        result = await self._session.execute(
            select(ProductModel).where(
                ProductModel.order_id == order_id,
                ProductModel.part_number == part_number,
            )
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_in_order_by_item(
        self, order_id: int, item: str
    ) -> Optional[Product]:
        result = await self._session.execute(
            select(ProductModel).where(
                ProductModel.order_id == order_id,
                ProductModel.item == item,
            )
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def create(self, product: Product) -> Product:
        model = ProductModel(**{f: getattr(product, f) for f in _ENTITY_FIELDS})
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, product_id: int, changes: dict) -> Product:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()
        for field, value in changes.items():
            setattr(model, field, value)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)
