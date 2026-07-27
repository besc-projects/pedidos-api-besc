from __future__ import annotations

from typing import Optional

import pytest

from app.application.use_cases.history_process.use_cases import (
    CreateHistoryProcessUseCase,
    ListHistoryProcessByOrderUseCase,
    ListHistoryProcessByStepUseCase,
    ListHistoryProcessUseCase,
)
from app.domain.entities.history_process_entry import HistoryProcessEntry
from app.domain.exceptions import ConflictException, NotFoundException
from app.schemas.history_process import HistoryProcessCreate


class FakeHistoryProcessRepository:
    def __init__(self) -> None:
        self._items: list[HistoryProcessEntry] = []
        self._next_id = 1

    async def get_by_order_and_description(
        self, order_id: int, description: str
    ) -> Optional[HistoryProcessEntry]:
        return next(
            (
                e
                for e in self._items
                if e.order_id == order_id and e.description == description
            ),
            None,
        )

    async def count(self) -> int:
        return len(self._items)

    async def list(self, skip: int, limit: int) -> list[HistoryProcessEntry]:
        return self._items[skip : skip + limit]

    async def list_by_order(self, order_id: int) -> list[HistoryProcessEntry]:
        return [e for e in self._items if e.order_id == order_id]

    async def list_by_step(
        self, order_id: int, step: str
    ) -> list[HistoryProcessEntry]:
        return [
            e for e in self._items if e.order_id == order_id and e.step == step
        ]

    async def create(self, entry: HistoryProcessEntry) -> HistoryProcessEntry:
        entry.id = self._next_id
        self._next_id += 1
        self._items.append(entry)
        return entry


def _payload(**overrides) -> HistoryProcessCreate:
    data = {"order_id": 1, "step": "cadastro", "description": "created"}
    data.update(overrides)
    return HistoryProcessCreate.model_validate(data)


async def test_create_history_ok():
    repository = FakeHistoryProcessRepository()
    entry = await CreateHistoryProcessUseCase(repository).execute(_payload())
    assert entry.id == 1
    assert entry.severity == "info"


async def test_create_duplicate_history():
    repository = FakeHistoryProcessRepository()
    use_case = CreateHistoryProcessUseCase(repository)
    await use_case.execute(_payload())
    with pytest.raises(ConflictException):
        await use_case.execute(_payload())


async def test_list_returns_total():
    repository = FakeHistoryProcessRepository()
    await CreateHistoryProcessUseCase(repository).execute(_payload())
    total, items = await ListHistoryProcessUseCase(repository).execute(0, 10)
    assert total == 1
    assert len(items) == 1


async def test_list_by_order_not_found():
    with pytest.raises(NotFoundException):
        await ListHistoryProcessByOrderUseCase(
            FakeHistoryProcessRepository()
        ).execute(999)


async def test_list_by_step_not_found():
    with pytest.raises(NotFoundException):
        await ListHistoryProcessByStepUseCase(
            FakeHistoryProcessRepository()
        ).execute(1, "x")
