from __future__ import annotations

from typing import Optional

import pytest

from app.application.use_cases.tickets.use_cases import (
    CreateTicketUseCase,
    DeleteTicketUseCase,
    GetTicketUseCase,
    UpdateTicketUseCase,
)
from app.domain.entities.ticket import Ticket
from app.domain.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.schemas.ticket.base import TicketCreate, TicketUpdate


class FakeTicketRepository:
    def __init__(self, internal_order_id: Optional[int] = 1) -> None:
        self._items: list[Ticket] = []
        self._statuses: set[int] = set()
        self._next_id = 1
        self._internal_order_id = internal_order_id

    async def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        return next((t for t in self._items if t.id == ticket_id), None)

    async def get_by_number(self, ticket_number: int) -> Optional[Ticket]:
        return next(
            (t for t in self._items if t.ticket_number == ticket_number), None
        )

    async def list(self, skip, limit, status_id, ticket_number, purchase_order):
        return self._items[skip : skip + limit]

    async def get_internal_order_id(self, purchase_order: int) -> Optional[int]:
        return self._internal_order_id

    async def status_exists(self, status_id: int) -> bool:
        return status_id in self._statuses

    async def create_status(self, status_id: int, name: str, description: str) -> None:
        self._statuses.add(status_id)

    async def create(self, ticket: Ticket) -> Ticket:
        ticket.id = self._next_id
        self._next_id += 1
        self._items.append(ticket)
        return ticket

    async def update(self, ticket_id: int, changes: dict) -> Ticket:
        ticket = next(t for t in self._items if t.id == ticket_id)
        for field, value in changes.items():
            setattr(ticket, field, value)
        return ticket

    async def delete(self, ticket_id: int) -> bool:
        target = next((t for t in self._items if t.id == ticket_id), None)
        if target is None:
            return False
        self._items.remove(target)
        return True


def _payload(**overrides) -> TicketCreate:
    data = {"ticket_number": 100, "purchase_order": 5000, "status_id": 0}
    data.update(overrides)
    return TicketCreate.model_validate(data)


async def test_create_ticket_ok():
    repository = FakeTicketRepository(internal_order_id=9)
    ticket = await CreateTicketUseCase(repository).execute(_payload())
    assert ticket.id == 1
    assert ticket.order_id == 9


async def test_create_ticket_duplicate_number():
    repository = FakeTicketRepository()
    use_case = CreateTicketUseCase(repository)
    await use_case.execute(_payload())
    with pytest.raises(ConflictException):
        await use_case.execute(_payload())


async def test_create_ticket_order_not_found():
    repository = FakeTicketRepository(internal_order_id=None)
    with pytest.raises(NotFoundException):
        await CreateTicketUseCase(repository).execute(_payload())


async def test_create_ticket_invalid_status():
    repository = FakeTicketRepository()
    with pytest.raises(ValidationException):
        await CreateTicketUseCase(repository).execute(_payload(status_id=99))


async def test_update_sets_observer_date_when_concluded():
    repository = FakeTicketRepository()
    created = await CreateTicketUseCase(repository).execute(_payload())
    message, changed, ticket = await UpdateTicketUseCase(repository).execute(
        created.id, TicketUpdate(status_id=2)
    )
    assert "status_id" in changed
    assert "observer_range_date" in changed
    assert ticket.observer_range_date is not None


async def test_update_no_changes():
    repository = FakeTicketRepository()
    created = await CreateTicketUseCase(repository).execute(_payload())
    message, changed, _ = await UpdateTicketUseCase(repository).execute(
        created.id, TicketUpdate(status_id=0)
    )
    assert message == "No changes detected"
    assert changed == []


async def test_get_ticket_not_found():
    with pytest.raises(NotFoundException):
        await GetTicketUseCase(FakeTicketRepository()).execute(123)


async def test_delete_ticket_not_found():
    with pytest.raises(NotFoundException):
        await DeleteTicketUseCase(FakeTicketRepository()).execute(1)
