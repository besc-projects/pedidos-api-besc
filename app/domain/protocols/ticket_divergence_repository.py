from __future__ import annotations

from typing import Optional, Protocol

from app.domain.entities.ticket_divergence import TicketDivergence


class TicketDivergenceRepositoryProtocol(Protocol):
    """Persistence contract for ticket divergences."""

    async def ticket_exists(self, ticket_id: int) -> bool:
        ...

    async def ticket_exists_by_number(self, ticket_number: int) -> bool:
        ...

    async def get_by_line_and_item(
        self, ticket_id: int, purchase_order_line: int, item_id: int
    ) -> Optional[TicketDivergence]:
        ...

    async def get_duplicate(
        self, purchase_order_line: int, item_id: int
    ) -> Optional[TicketDivergence]:
        ...

    async def list_by_ticket(self, ticket_id: int) -> list[TicketDivergence]:
        ...

    async def list_item_ids_by_ticket_number(
        self, ticket_number: int
    ) -> list[int]:
        ...

    async def create(self, divergence: TicketDivergence) -> TicketDivergence:
        ...

    async def update(self, divergence_id: int, changes: dict) -> TicketDivergence:
        ...

    async def delete(
        self, ticket_id: int, purchase_order_line: int, item_id: int
    ) -> bool:
        ...
