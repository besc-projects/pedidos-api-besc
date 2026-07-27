from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.ticket_progress import TicketProgress
from app.models.tickets import Ticket as TicketModel
from app.models.tickets import TicketProgress as TicketProgressModel


class SqlAlchemyTicketProgressRepository:
    """SQLAlchemy persistence for ticket progress steps."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: TicketProgressModel) -> TicketProgress:
        return TicketProgress(
            id=model.id,
            ticket_id=model.ticket_id,
            status_progress_id=model.status_progress_id,
            start_date=model.start_date,
            end_date=model.end_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def ticket_exists(self, ticket_id: int) -> bool:
        return await self._session.get(TicketModel, ticket_id) is not None

    async def list_by_ticket(self, ticket_id: int) -> list[TicketProgress]:
        result = await self._session.execute(
            select(TicketProgressModel).where(
                TicketProgressModel.ticket_id == ticket_id
            )
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def get(
        self, ticket_id: int, progress_id: int
    ) -> Optional[TicketProgress]:
        result = await self._session.execute(
            select(TicketProgressModel).where(
                TicketProgressModel.id == progress_id,
                TicketProgressModel.ticket_id == ticket_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, progress: TicketProgress) -> TicketProgress:
        model = TicketProgressModel(
            ticket_id=progress.ticket_id,
            status_progress_id=progress.status_progress_id,
            start_date=progress.start_date,
            end_date=progress.end_date,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, progress_id: int, changes: dict) -> TicketProgress:
        result = await self._session.execute(
            select(TicketProgressModel).where(TicketProgressModel.id == progress_id)
        )
        model = result.scalar_one_or_none()
        for field, value in changes.items():
            setattr(model, field, value)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete_all(self, ticket_id: int) -> int:
        result = await self._session.execute(
            delete(TicketProgressModel).where(
                TicketProgressModel.ticket_id == ticket_id
            )
        )
        await self._session.flush()
        return result.rowcount or 0
