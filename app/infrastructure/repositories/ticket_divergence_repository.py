from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.ticket_divergence import TicketDivergence
from app.models.tickets import Ticket as TicketModel
from app.models.tickets import TicketDivergence as TicketDivergenceModel


class SqlAlchemyTicketDivergenceRepository:
    """SQLAlchemy persistence for ticket divergences."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: TicketDivergenceModel) -> TicketDivergence:
        return TicketDivergence(
            id=model.id,
            ticket_id=model.ticket_id,
            item_id=model.item_id,
            purchase_order_line=model.purchase_order_line,
            legal_basis=model.legal_basis,
            taxes=model.taxes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def ticket_exists(self, ticket_id: int) -> bool:
        return await self._session.get(TicketModel, ticket_id) is not None

    async def ticket_exists_by_number(self, ticket_number: int) -> bool:
        result = await self._session.execute(
            select(TicketModel.id).where(TicketModel.ticket_number == ticket_number)
        )
        return result.scalar_one_or_none() is not None

    async def get_by_line_and_item(
        self, ticket_id: int, purchase_order_line: int, item_id: int
    ) -> Optional[TicketDivergence]:
        result = await self._session.execute(
            select(TicketDivergenceModel).where(
                TicketDivergenceModel.purchase_order_line == purchase_order_line,
                TicketDivergenceModel.item_id == item_id,
                TicketDivergenceModel.ticket_id == ticket_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_duplicate(
        self, purchase_order_line: int, item_id: int
    ) -> Optional[TicketDivergence]:
        result = await self._session.execute(
            select(TicketDivergenceModel).where(
                TicketDivergenceModel.purchase_order_line == purchase_order_line,
                TicketDivergenceModel.item_id == item_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_ticket(self, ticket_id: int) -> list[TicketDivergence]:
        result = await self._session.execute(
            select(TicketDivergenceModel).where(
                TicketDivergenceModel.ticket_id == ticket_id
            )
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_item_ids_by_ticket_number(
        self, ticket_number: int
    ) -> list[int]:
        result = await self._session.execute(
            select(TicketDivergenceModel.item_id)
            .join(TicketModel)
            .where(TicketModel.ticket_number == ticket_number)
        )
        return list(result.scalars().all())

    async def create(self, divergence: TicketDivergence) -> TicketDivergence:
        model = TicketDivergenceModel(
            ticket_id=divergence.ticket_id,
            item_id=divergence.item_id,
            purchase_order_line=divergence.purchase_order_line,
            legal_basis=divergence.legal_basis,
            taxes=divergence.taxes,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, divergence_id: int, changes: dict) -> TicketDivergence:
        result = await self._session.execute(
            select(TicketDivergenceModel).where(
                TicketDivergenceModel.id == divergence_id
            )
        )
        model = result.scalar_one_or_none()
        for field, value in changes.items():
            setattr(model, field, value)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(
        self, ticket_id: int, purchase_order_line: int, item_id: int
    ) -> bool:
        result = await self._session.execute(
            select(TicketDivergenceModel).where(
                TicketDivergenceModel.purchase_order_line == purchase_order_line,
                TicketDivergenceModel.item_id == item_id,
                TicketDivergenceModel.ticket_id == ticket_id,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
