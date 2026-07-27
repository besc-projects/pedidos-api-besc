from __future__ import annotations

from app.domain.entities.ticket_divergence import TicketDivergence
from app.domain.exceptions import ConflictException, NotFoundException
from app.domain.protocols.ticket_divergence_repository import (
    TicketDivergenceRepositoryProtocol,
)
from app.schemas.ticket.divergence import (
    TicketDivergenceCreate,
    TicketDivergenceUpdate,
)


class CreateTicketDivergenceUseCase:
    def __init__(self, repository: TicketDivergenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, ticket_id: int, data: TicketDivergenceCreate
    ) -> TicketDivergence:
        if not await self._repository.ticket_exists(ticket_id):
            raise NotFoundException("Ticket not found.")

        duplicate = await self._repository.get_duplicate(
            data.purchase_order_line, data.item_id
        )
        if duplicate is not None:
            raise ConflictException(
                f"Divergence '{data.purchase_order_line}/{data.item_id}' "
                "already exists."
            )

        divergence = TicketDivergence(
            ticket_id=ticket_id,
            item_id=data.item_id,
            purchase_order_line=data.purchase_order_line,
            legal_basis=data.legal_basis,
            taxes=data.taxes,
        )
        return await self._repository.create(divergence)


class ListTicketDivergencesUseCase:
    def __init__(self, repository: TicketDivergenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, ticket_id: int) -> list[TicketDivergence]:
        return await self._repository.list_by_ticket(ticket_id)


class GetDivergenceItemIdsByTicketNumberUseCase:
    def __init__(self, repository: TicketDivergenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, ticket_number: int) -> list[int]:
        item_ids = await self._repository.list_item_ids_by_ticket_number(
            ticket_number
        )
        if item_ids:
            return item_ids
        if not await self._repository.ticket_exists_by_number(ticket_number):
            raise NotFoundException("Ticket not found.")
        return []


class UpdateTicketDivergenceUseCase:
    def __init__(self, repository: TicketDivergenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self,
        ticket_id: int,
        purchase_order_line: int,
        item_id: int,
        data: TicketDivergenceUpdate,
    ) -> TicketDivergence:
        divergence = await self._repository.get_by_line_and_item(
            ticket_id, purchase_order_line, item_id
        )
        if divergence is None:
            raise NotFoundException("Divergence not found.")
        changes = data.model_dump(exclude_unset=True)
        return await self._repository.update(divergence.id, changes)


class DeleteTicketDivergenceUseCase:
    def __init__(self, repository: TicketDivergenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, ticket_id: int, purchase_order_line: int, item_id: int
    ) -> None:
        deleted = await self._repository.delete(
            ticket_id, purchase_order_line, item_id
        )
        if not deleted:
            raise NotFoundException("Divergence not found.")
