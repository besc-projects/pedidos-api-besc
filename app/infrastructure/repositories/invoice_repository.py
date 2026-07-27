from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.invoice import Invoice
from app.models.invoices import Invoice as InvoiceModel


class SqlAlchemyInvoiceRepository:
    """SQLAlchemy implementation of the invoice persistence contract."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: InvoiceModel) -> Invoice:
        return Invoice(
            id=model.id,
            order_id=model.order_id,
            supra_id=model.supra_id,
            issue_code=model.issue_code,
            transmission_code=model.transmission_code,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        result = await self._session.execute(
            select(InvoiceModel).where(InvoiceModel.id == invoice_id)
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_by_order_id(self, order_id: int) -> Optional[Invoice]:
        result = await self._session.execute(
            select(InvoiceModel).where(InvoiceModel.order_id == order_id)
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def list(
        self,
        order_id: Optional[int] = None,
        pending_transmission: Optional[bool] = None,
    ) -> list[Invoice]:
        query = select(InvoiceModel)
        if order_id is not None:
            query = query.where(InvoiceModel.order_id == order_id)
        if pending_transmission is True:
            query = query.where(InvoiceModel.transmission_code.is_(None))
        elif pending_transmission is False:
            query = query.where(InvoiceModel.transmission_code.is_not(None))

        result = await self._session.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def create(self, invoice: Invoice) -> Invoice:
        model = InvoiceModel(
            order_id=invoice.order_id,
            supra_id=invoice.supra_id,
            issue_code=invoice.issue_code,
            transmission_code=invoice.transmission_code,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, invoice: Invoice) -> Invoice:
        result = await self._session.execute(
            select(InvoiceModel).where(InvoiceModel.id == invoice.id)
        )
        model = result.scalars().first()

        model.transmission_code = invoice.transmission_code

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)
