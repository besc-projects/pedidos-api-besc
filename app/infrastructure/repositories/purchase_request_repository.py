from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.purchase_request import PurchaseRequest
from app.domain.enums.purchase_request_status import PurchaseRequestStatus
from app.models.purchase_requests import PurchaseRequest as PurchaseRequestModel


class SqlAlchemyPurchaseRequestRepository:
    """SQLAlchemy implementation of the purchase-request persistence contract.

    It only reads and writes data; it holds no business rules. Domain entities
    are mapped to and from ORM models at this boundary.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: PurchaseRequestModel) -> PurchaseRequest:
        return PurchaseRequest(
            id=model.id,
            order_id=model.order_id,
            product_id=model.product_id,
            part_number=model.part_number,
            supplier_product_code=model.supplier_product_code,
            released_quantity=float(model.released_quantity),
            requested_quantity=float(model.requested_quantity),
            status=PurchaseRequestStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(
        self, purchase_request_id: int
    ) -> Optional[PurchaseRequest]:
        result = await self._session.execute(
            select(PurchaseRequestModel).where(
                PurchaseRequestModel.id == purchase_request_id
            )
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_by_order_and_part_number(
        self, order_id: int, part_number: str
    ) -> Optional[PurchaseRequest]:
        result = await self._session.execute(
            select(PurchaseRequestModel).where(
                PurchaseRequestModel.order_id == order_id,
                PurchaseRequestModel.part_number == part_number,
            )
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def list_by_order(
        self, order_id: int, status: Optional[PurchaseRequestStatus] = None
    ) -> list[PurchaseRequest]:
        query = select(PurchaseRequestModel).where(
            PurchaseRequestModel.order_id == order_id
        )
        if status is not None:
            query = query.where(PurchaseRequestModel.status == status)

        result = await self._session.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_all(
        self, status: Optional[PurchaseRequestStatus] = None
    ) -> list[PurchaseRequest]:
        query = select(PurchaseRequestModel)
        if status is not None:
            query = query.where(PurchaseRequestModel.status == status)

        result = await self._session.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def create(self, purchase_request: PurchaseRequest) -> PurchaseRequest:
        model = PurchaseRequestModel(
            order_id=purchase_request.order_id,
            product_id=purchase_request.product_id,
            part_number=purchase_request.part_number,
            supplier_product_code=purchase_request.supplier_product_code,
            released_quantity=purchase_request.released_quantity,
            requested_quantity=purchase_request.requested_quantity,
            status=purchase_request.status,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, purchase_request: PurchaseRequest) -> PurchaseRequest:
        result = await self._session.execute(
            select(PurchaseRequestModel).where(
                PurchaseRequestModel.id == purchase_request.id
            )
        )
        model = result.scalars().first()

        model.released_quantity = purchase_request.released_quantity
        model.requested_quantity = purchase_request.requested_quantity
        model.status = purchase_request.status

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)
