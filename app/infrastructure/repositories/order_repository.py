from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.order import Order
from app.domain.entities.product import Product
from app.models.orders import Order as OrderModel
from app.models.products import Product as ProductModel
from app.models.tax_reference import TaxReferenceProductSupra as TaxReferenceModel

_ORDER_FIELDS = (
    "vale_order_id",
    "total_value",
    "cnpj",
    "date",
    "process_id",
    "status_code",
    "state",
    "ticket_id",
    "portal",
    "center",
    "besc_order_id",
    "contract_number",
    "invoice_number",
    "days_to_delivery",
    "version",
)

_PRODUCT_FIELDS = (
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


class SqlAlchemyOrderRepository:
    """SQLAlchemy persistence for purchase orders."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: OrderModel) -> Order:
        values = {field: getattr(model, field) for field in _ORDER_FIELDS}
        # process_id/status_code podem ser NULL no banco (dado legado); o
        # domínio sempre espera um código válido, então normaliza pra 0 aqui,
        # na borda de persistência — mesmo comportamento do serviço legado.
        values["process_id"] = values["process_id"] or 0
        values["status_code"] = values["status_code"] or 0
        return Order(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            **values,
        )

    @staticmethod
    def _product_to_entity(model: ProductModel) -> Product:
        return Product(
            id=model.id, **{field: getattr(model, field) for field in _PRODUCT_FIELDS}
        )

    async def _products_for(self, order_id: int) -> list[Product]:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.order_id == order_id)
        )
        return [self._product_to_entity(model) for model in result.scalars().all()]

    async def create(self, order: Order) -> Order:
        model = OrderModel(**{field: getattr(order, field) for field in _ORDER_FIELDS})
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_with_products(
        self, vale_order_id: int
    ) -> Optional[tuple[Order, list[Product]]]:
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.vale_order_id == vale_order_id)
        )
        model = result.scalars().first()
        if model is None:
            return None
        products = await self._products_for(model.id)
        return self._to_entity(model), products

    async def list_by_process_status(
        self, process_id: int, status_code: int, skip: int, limit: int
    ) -> list[tuple[Order, list[Product]]]:
        result = await self._session.execute(
            select(OrderModel)
            .where(
                OrderModel.process_id == process_id,
                OrderModel.status_code == status_code,
            )
            .order_by(OrderModel.id)
            .offset(skip)
            .limit(limit)
        )
        orders = result.scalars().unique().all()
        return [
            (self._to_entity(model), await self._products_for(model.id))
            for model in orders
        ]

    async def list_with_tax_reference(
        self, vale_order_id: Optional[int], skip: int, limit: int
    ) -> list[dict]:
        query = (
            select(OrderModel, ProductModel, TaxReferenceModel)
            .join(ProductModel, ProductModel.order_id == OrderModel.id)
            .join(
                TaxReferenceModel,
                TaxReferenceModel.id_product == ProductModel.id,
            )
            .where(OrderModel.process_id == 2, OrderModel.status_code == 1)
            .order_by(OrderModel.id, ProductModel.id)
            .offset(skip)
            .limit(limit)
        )
        if vale_order_id is not None:
            query = query.where(OrderModel.vale_order_id == vale_order_id)

        result = await self._session.execute(query)

        orders_map: dict[int, dict] = {}
        seen_products: dict[int, set] = {}
        for order, product, tax_ref in result.all():
            if order.id not in orders_map:
                orders_map[order.id] = {
                    "vale_order_id": int(order.vale_order_id),
                    "state": str(order.state or "").strip().upper(),
                    "products": [],
                    "besc_order_id": order.besc_order_id,
                    "invoice_number": order.invoice_number,
                    "center": order.center,
                }
                seen_products[order.id] = set()

            if tax_ref.id_product in seen_products[order.id]:
                continue
            seen_products[order.id].add(tax_ref.id_product)

            orders_map[order.id]["products"].append(
                {
                    "product_id": product.id,
                    "item": product.item,
                    "part_number": product.part_number,
                    "description": product.description,
                    "ncm_code": tax_ref.ncm_code,
                    "ipi": float(tax_ref.ipi) if tax_ref.ipi is not None else None,
                    "icms": float(tax_ref.icms) if tax_ref.icms is not None else None,
                    "icms_st": (
                        float(tax_ref.icms_st)
                        if tax_ref.icms_st is not None
                        else None
                    ),
                    "origin": tax_ref.origin,
                    "id_product": tax_ref.id_product,
                    "tax_reference_id": tax_ref.id,
                    "created_at": tax_ref.created_at,
                    "updated_at": tax_ref.updated_at,
                }
            )

        return list(orders_map.values())

    async def update_by_vale(
        self, vale_order_id: int, changes: dict
    ) -> Optional[Order]:
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.vale_order_id == vale_order_id)
        )
        model = result.scalars().first()
        if model is None:
            return None
        for field, value in changes.items():
            if hasattr(model, field):
                setattr(model, field, value)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def set_status_by_vale(
        self, vale_order_id: int, process_id: int, status_code: int
    ) -> Optional[Order]:
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.vale_order_id == vale_order_id)
        )
        model = result.scalars().first()
        if model is None:
            return None
        model.process_id = process_id
        model.status_code = status_code
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete_by_id(self, order_id: int) -> bool:
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        model = result.scalars().first()
        if model is None:
            return False
        await self._session.execute(
            delete(ProductModel).where(ProductModel.order_id == order_id)
        )
        await self._session.delete(model)
        await self._session.flush()
        return True
