from __future__ import annotations

from typing import Optional, Protocol

from app.domain.entities.ticket_progress import TicketProgress


class TicketProgressRepositoryProtocol(Protocol):
    """Persistence contract for ticket progress steps."""

    async def ticket_exists(self, ticket_id: int) -> bool:
        ...

    async def list_by_ticket(self, ticket_id: int) -> list[TicketProgress]:
        ...

    async def get(
        self, ticket_id: int, progress_id: int
    ) -> Optional[TicketProgress]:
        ...

    async def create(self, progress: TicketProgress) -> TicketProgress:
        ...

    async def update(self, progress_id: int, changes: dict) -> TicketProgress:
        ...

    async def delete_all(self, ticket_id: int) -> int:
        ...
