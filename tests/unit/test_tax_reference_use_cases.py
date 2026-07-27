from __future__ import annotations

from typing import Optional

import pytest

from app.application.use_cases.tax_reference.use_cases import (
    CreateTaxReferenceUseCase,
    DeleteTaxReferenceUseCase,
    GetTaxReferenceByOrderUseCase,
    GetTaxReferenceByProductUseCase,
    GetTaxReferenceUseCase,
    UpdateTaxReferenceUseCase,
)
from app.domain.entities.tax_reference import TaxReference
from app.domain.exceptions import NotFoundException
from app.schemas.tax_reference import TaxReferenceCreate, TaxReferenceUpdate


class FakeTaxReferenceRepository:
    def __init__(self) -> None:
        self._items: list[TaxReference] = []
        self._next_id = 1

    async def get_by_id(self, entry_id: int) -> Optional[TaxReference]:
        return next((e for e in self._items if e.id == entry_id), None)

    async def list_by_product(self, id_product: int) -> list[TaxReference]:
        return [e for e in self._items if e.id_product == id_product]

    async def list_by_order(self, vale_order_id: int) -> list[TaxReference]:
        return []

    async def list(self, skip: int, limit: int) -> list[TaxReference]:
        return self._items[skip : skip + limit]

    async def create(self, tax_reference: TaxReference) -> TaxReference:
        tax_reference.id = self._next_id
        self._next_id += 1
        self._items.append(tax_reference)
        return tax_reference

    async def update(self, tax_reference: TaxReference, changes: dict) -> TaxReference:
        for field, value in changes.items():
            setattr(tax_reference, field, value)
        return tax_reference

    async def delete(self, entry_id: int) -> bool:
        target = next((e for e in self._items if e.id == entry_id), None)
        if target is None:
            return False
        self._items.remove(target)
        return True


def _payload(**overrides) -> TaxReferenceCreate:
    data = {"id_product": 10, "ncm_code": "1234567890"}
    data.update(overrides)
    return TaxReferenceCreate.model_validate(data)


async def test_create_tax_reference():
    repository = FakeTaxReferenceRepository()
    entry = await CreateTaxReferenceUseCase(repository).execute(_payload())
    assert entry.id == 1


async def test_get_not_found():
    with pytest.raises(NotFoundException):
        await GetTaxReferenceUseCase(FakeTaxReferenceRepository()).execute(1)


async def test_get_by_product_not_found():
    with pytest.raises(NotFoundException):
        await GetTaxReferenceByProductUseCase(
            FakeTaxReferenceRepository()
        ).execute(99)


async def test_get_by_order_not_found():
    with pytest.raises(NotFoundException):
        await GetTaxReferenceByOrderUseCase(
            FakeTaxReferenceRepository()
        ).execute(99)


async def test_update_applies_changes():
    repository = FakeTaxReferenceRepository()
    created = await CreateTaxReferenceUseCase(repository).execute(_payload())
    updated = await UpdateTaxReferenceUseCase(repository).execute(
        created.id, TaxReferenceUpdate(ncm_code="9999999999")
    )
    assert updated.ncm_code == "9999999999"


async def test_delete_not_found():
    with pytest.raises(NotFoundException):
        await DeleteTaxReferenceUseCase(FakeTaxReferenceRepository()).execute(1)
