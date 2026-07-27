from __future__ import annotations

from app.domain.entities.ticket_progress import TicketProgress
from app.domain.exceptions import NotFoundException
from app.domain.protocols.ticket_progress_repository import (
    TicketProgressRepositoryProtocol,
)
from app.schemas.ticket.progress import (
    TicketProgressCreate,
    TicketProgressUpdate,
)


class CreateTicketProgressUseCase:
    def __init__(self, repository: TicketProgressRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, ticket_id: int, data: TicketProgressCreate
    ) -> TicketProgress:
        if not await self._repository.ticket_exists(ticket_id):
            raise NotFoundException("Ticket not found.")
        progress = TicketProgress(ticket_id=ticket_id, **data.model_dump())
        return await self._repository.create(progress)


class ListTicketProgressesUseCase:
    def __init__(self, repository: TicketProgressRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, ticket_id: int) -> list[TicketProgress]:
        return await self._repository.list_by_ticket(ticket_id)


class UpdateTicketProgressUseCase:
    def __init__(self, repository: TicketProgressRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, ticket_id: int, progress_id: int, data: TicketProgressUpdate
    ) -> TicketProgress:
        progress = await self._repository.get(ticket_id, progress_id)
        if progress is None:
            raise NotFoundException("Progress not found.")
        changes = data.model_dump(exclude_unset=True)
        return await self._repository.update(progress_id, changes)


class DeleteAllTicketProgressesUseCase:
    def __init__(self, repository: TicketProgressRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, ticket_id: int) -> int:
        deleted = await self._repository.delete_all(ticket_id)
        if deleted == 0:
            raise NotFoundException("Progress not found.")
        return deleted
