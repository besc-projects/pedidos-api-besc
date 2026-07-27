from __future__ import annotations

from typing import Optional

from app.domain.entities.ticket import Ticket
from app.domain.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.domain.protocols.ticket_repository import TicketRepositoryProtocol
from app.schemas.ticket.base import TicketCreate, TicketUpdate

DEFAULT_TICKET_STATUSES: dict[int, tuple[str, str]] = {
    0: ("EM_ABERTO", "Em aberto"),
    1: ("EM_ANDAMENTO", "Em andamento"),
    2: ("CONCLUIDO", "Concluido"),
    3: ("REABERTO", "Reaberto"),
}


async def _ensure_status(
    repository: TicketRepositoryProtocol, status_id: Optional[int]
) -> None:
    if status_id is None or await repository.status_exists(status_id):
        return
    default = DEFAULT_TICKET_STATUSES.get(status_id)
    if default is None:
        raise ValidationException(
            f"Invalid status_id '{status_id}'. Create this status first."
        )
    await repository.create_status(status_id, *default)


async def _ensure_number_unique(
    repository: TicketRepositoryProtocol,
    ticket_number: Optional[int],
    current_id: Optional[int] = None,
) -> None:
    if ticket_number is None:
        return
    existing = await repository.get_by_number(ticket_number)
    if existing is not None and existing.id != current_id:
        raise ConflictException(f"Ticket number '{ticket_number}' already exists.")


class CreateTicketUseCase:
    """Create a ticket, linking it to its order and ensuring its status."""

    def __init__(self, repository: TicketRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: TicketCreate) -> Ticket:
        await _ensure_number_unique(self._repository, data.ticket_number)
        await _ensure_status(self._repository, data.status_id)

        internal_order_id = await self._repository.get_internal_order_id(
            data.purchase_order
        )
        if internal_order_id is None:
            raise NotFoundException(
                f"Order with purchase order '{data.purchase_order}' not found."
            )

        ticket = Ticket(
            order_id=internal_order_id,
            ticket_number=data.ticket_number,
            purchase_order=data.purchase_order,
            opened_at=data.opened_at,
            closed_at=data.closed_at,
            observer_range_date=data.observer_range_date,
            status_id=data.status_id,
            notes=data.notes,
        )
        return await self._repository.create(ticket)


class ListTicketsUseCase:
    """List tickets with optional filters."""

    def __init__(self, repository: TicketRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self,
        skip: int,
        limit: int,
        status_id: Optional[int],
        ticket_number: Optional[int],
        purchase_order: Optional[int],
    ) -> list[Ticket]:
        return await self._repository.list(
            skip, limit, status_id, ticket_number, purchase_order
        )


class GetTicketUseCase:
    """Retrieve a ticket by its number."""

    def __init__(self, repository: TicketRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, ticket_number: int) -> Ticket:
        ticket = await self._repository.get_by_number(ticket_number)
        if ticket is None:
            raise NotFoundException("Ticket not found.")
        return ticket


class UpdateTicketUseCase:
    """Update a ticket, returning the message, changed fields and ticket."""

    def __init__(self, repository: TicketRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, ticket_id: int, data: TicketUpdate
    ) -> tuple[str, list[str], Ticket]:
        ticket = await self._repository.get_by_id(ticket_id)
        if ticket is None:
            raise NotFoundException("Ticket not found.")

        changes = data.model_dump(exclude_unset=True)
        if "ticket_number" in changes:
            await _ensure_number_unique(
                self._repository, changes["ticket_number"], current_id=ticket_id
            )
        if "status_id" in changes:
            await _ensure_status(self._repository, changes["status_id"])

        changed_fields = [
            field
            for field, value in changes.items()
            if getattr(ticket, field) != value
        ]
        if not changed_fields:
            return "No changes detected", [], ticket

        applied = {field: changes[field] for field in changed_fields}
        for field, value in applied.items():
            setattr(ticket, field, value)

        if (
            "status_id" in changed_fields
            and "observer_range_date" not in changed_fields
            and ticket.is_concluded()
        ):
            ticket.observer_range_date = Ticket.today_iso()
            applied["observer_range_date"] = ticket.observer_range_date
            changed_fields.append("observer_range_date")

        updated = await self._repository.update(ticket_id, applied)
        return "Ticket updated successfully", changed_fields, updated


class DeleteTicketUseCase:
    """Delete a ticket by id."""

    def __init__(self, repository: TicketRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, ticket_id: int) -> None:
        deleted = await self._repository.delete(ticket_id)
        if not deleted:
            raise NotFoundException("Ticket not found.")
