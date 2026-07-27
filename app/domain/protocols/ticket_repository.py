from __future__ import annotations

from typing import Optional, Protocol

from app.domain.entities.ticket import Ticket


class TicketRepositoryProtocol(Protocol):
    """Persistence contract for support tickets."""

    async def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        ...

    async def get_by_number(self, ticket_number: int) -> Optional[Ticket]:
        ...

    async def list(
        self,
        skip: int,
        limit: int,
        status_id: Optional[int],
        ticket_number: Optional[int],
        purchase_order: Optional[int],
    ) -> list[Ticket]:
        ...

    async def get_internal_order_id(self, purchase_order: int) -> Optional[int]:
        ...

    async def status_exists(self, status_id: int) -> bool:
        ...

    async def create_status(
        self, status_id: int, name: str, description: str
    ) -> None:
        ...

    async def create(self, ticket: Ticket) -> Ticket:
        ...

    async def update(self, ticket_id: int, changes: dict) -> Ticket:
        ...

    async def delete(self, ticket_id: int) -> bool:
        ...
