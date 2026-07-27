from typing import Optional

import pytest

from app.application.use_cases.price_table.use_cases import (
    CheckPnExistsUseCase,
    CreatePriceTableEntryUseCase,
    DeletePriceTableEntryUseCase,
    GetPriceByPnUseCase,
    UpdatePriceTableEntryUseCase,
)
from app.domain.entities.price_table_entry import PriceTableEntry
from app.domain.exceptions import ConflictException, NotFoundException
from app.schemas.price_table import PriceTableCreate, PriceTableUpdate


class FakePriceTableRepository:
    def __init__(self) -> None:
        self._items: list[PriceTableEntry] = []
        self._next_id = 1

    async def get_by_id(self, entry_id: int) -> Optional[PriceTableEntry]:
        return next((e for e in self._items if e.id == entry_id), None)

    async def get_by_pn_and_destination(
        self, pn: str, destination: str
    ) -> Optional[PriceTableEntry]:
        return next(
            (e for e in self._items if e.pn == pn and e.destination == destination),
            None,
        )

    async def list(self, skip: int, limit: int) -> list[PriceTableEntry]:
        return self._items[skip : skip + limit]

    async def create(self, entry: PriceTableEntry) -> PriceTableEntry:
        entry.id = self._next_id
        self._next_id += 1
        self._items.append(entry)
        return entry

    async def update(self, entry: PriceTableEntry, changes: dict) -> PriceTableEntry:
        for field, value in changes.items():
            setattr(entry, field, value)
        return entry

    async def delete(self, entry_id: int) -> bool:
        target = next((e for e in self._items if e.id == entry_id), None)
        if target is None:
            return False
        self._items.remove(target)
        return True


def _payload(**overrides) -> PriceTableCreate:
    data = {
        "pn": "PN1",
        "long_description": "long",
        "description": "desc",
        "destination": "mg",
        "unit_price": 10.0,
    }
    data.update(overrides)
    return PriceTableCreate.model_validate(data)


async def test_create_normalizes_destination():
    repository = FakePriceTableRepository()
    entry = await CreatePriceTableEntryUseCase(repository).execute(_payload())
    assert entry.destination == "MG"


async def test_create_duplicate_pn_destination():
    repository = FakePriceTableRepository()
    use_case = CreatePriceTableEntryUseCase(repository)
    await use_case.execute(_payload())
    with pytest.raises(ConflictException):
        await use_case.execute(_payload(destination="MG"))


async def test_get_price_by_pn_not_found():
    use_case = GetPriceByPnUseCase(FakePriceTableRepository())
    with pytest.raises(NotFoundException):
        await use_case.execute("PN1", "MG")


async def test_update_not_found():
    use_case = UpdatePriceTableEntryUseCase(FakePriceTableRepository())
    with pytest.raises(NotFoundException):
        await use_case.execute(1, PriceTableUpdate(unit_price=5))


async def test_delete_not_found():
    with pytest.raises(NotFoundException):
        await DeletePriceTableEntryUseCase(FakePriceTableRepository()).execute(1)


async def test_check_pn_exists():
    repository = FakePriceTableRepository()
    await CreatePriceTableEntryUseCase(repository).execute(_payload())
    assert await CheckPnExistsUseCase(repository).execute("PN1", "mg") is True
    assert await CheckPnExistsUseCase(repository).execute("PN2", "mg") is False
