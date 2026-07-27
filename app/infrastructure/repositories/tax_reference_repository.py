from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.tax_reference import TaxReference
from app.models.orders import Order as OrderModel
from app.models.products import Product as ProductModel
from app.models.tax_reference import TaxReferenceProductSupra as TaxReferenceModel


class SqlAlchemyTaxReferenceRepository:
    """SQLAlchemy persistence for product tax references."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: TaxReferenceModel) -> TaxReference:
        return TaxReference(
            id=model.id,
            id_product=model.id_product,
            ncm_code=model.ncm_code,
            ipi=model.ipi,
            icms=model.icms,
            icms_st=model.icms_st,
            origin=model.origin,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, entry_id: int) -> Optional[TaxReference]:
        result = await self._session.execute(
            select(TaxReferenceModel).where(TaxReferenceModel.id == entry_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_product(self, id_product: int) -> list[TaxReference]:
        result = await self._session.execute(
            select(TaxReferenceModel).where(
                TaxReferenceModel.id_product == id_product
            )
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_by_order(self, vale_order_id: int) -> list[TaxReference]:
        result = await self._session.execute(
            select(TaxReferenceModel)
            .join(ProductModel, TaxReferenceModel.id_product == ProductModel.id)
            .join(OrderModel, OrderModel.id == ProductModel.order_id)
            .where(OrderModel.vale_order_id == vale_order_id)
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list(self, skip: int, limit: int) -> list[TaxReference]:
        result = await self._session.execute(
            select(TaxReferenceModel).offset(skip).limit(limit)
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def create(self, tax_reference: TaxReference) -> TaxReference:
        model = TaxReferenceModel(
            id_product=tax_reference.id_product,
            ncm_code=tax_reference.ncm_code,
            ipi=tax_reference.ipi,
            icms=tax_reference.icms,
            icms_st=tax_reference.icms_st,
            origin=tax_reference.origin,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(
        self, tax_reference: TaxReference, changes: dict
    ) -> TaxReference:
        result = await self._session.execute(
            select(TaxReferenceModel).where(
                TaxReferenceModel.id == tax_reference.id
            )
        )
        model = result.scalar_one_or_none()
        for field, value in changes.items():
            setattr(model, field, value)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, entry_id: int) -> bool:
        result = await self._session.execute(
            select(TaxReferenceModel).where(TaxReferenceModel.id == entry_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
