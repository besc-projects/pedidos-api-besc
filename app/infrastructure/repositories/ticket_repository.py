from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.ticket import Ticket
from app.models.orders import Order as OrderModel
from app.models.tickets import Ticket as TicketModel
from app.models.status.tickets import TicketStatus as TicketStatusModel

_ENTITY_FIELDS = (
    "order_id",
    "ticket_number",
    "purchase_order",
    "opened_at",
    "closed_at",
    "observer_range_date",
    "status_id",
    "notes",
)


class SqlAlchemyTicketRepository:
    """SQLAlchemy persistence for support tickets."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: TicketModel) -> Ticket:
        return Ticket(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            **{field: getattr(model, field) for field in _ENTITY_FIELDS},
        )

    async def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_number(self, ticket_number: int) -> Optional[Ticket]:
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.ticket_number == ticket_number)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(
        self,
        skip: int,
        limit: int,
        status_id: Optional[int],
        ticket_number: Optional[int],
        purchase_order: Optional[int],
    ) -> list[Ticket]:
        query = select(TicketModel).offset(skip).limit(limit)
        if status_id is not None:
            query = query.where(TicketModel.status_id == status_id)
        if ticket_number is not None:
            query = query.where(TicketModel.ticket_number == ticket_number)
        if purchase_order is not None:
            query = query.where(TicketModel.purchase_order == purchase_order)

        result = await self._session.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def get_internal_order_id(self, purchase_order: int) -> Optional[int]:
        result = await self._session.execute(
            select(OrderModel.id).where(OrderModel.vale_order_id == purchase_order)
        )
        return result.scalar_one_or_none()

    async def status_exists(self, status_id: int) -> bool:
        result = await self._session.execute(
            select(TicketStatusModel.id).where(TicketStatusModel.id == status_id)
        )
        return result.scalar_one_or_none() is not None

    async def create_status(
        self, status_id: int, name: str, description: str
    ) -> None:
        self._session.add(
            TicketStatusModel(id=status_id, name=name, description=description)
        )
        await self._session.flush()

    async def create(self, ticket: Ticket) -> Ticket:
        model = TicketModel(
            **{field: getattr(ticket, field) for field in _ENTITY_FIELDS}
        )
        self._session.add(model)
        await self._session.flush()

        if ticket.order_id is not None:
            order = await self._session.get(OrderModel, ticket.order_id)
            if order is not None:
                order.ticket_id = model.id

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, ticket_id: int, changes: dict) -> Ticket:
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id)
        )
        model = result.scalar_one_or_none()
        for field, value in changes.items():
            setattr(model, field, value)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, ticket_id: int) -> bool:
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
