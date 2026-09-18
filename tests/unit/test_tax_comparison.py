from __future__ import annotations

import pytest

from app.application.use_cases.orders.use_cases import GetOrderTaxComparisonUseCase
from app.domain.services.tax_comparison import compare_fields


class FakeRepository:
    def __init__(self, items: list[dict]) -> None:
        self._items = items

    async def get_tax_comparison(self, vale_order_id: int) -> list[dict]:
        return self._items


def _item(declared: dict, correct: dict) -> dict:
    return {
        "item": "00010",
        "part_number": "EF04066",
        "description": "RELÉ DE ROTAÇÃO DE FASE",
        "declared": declared,
        "correct": correct,
    }


_BASE = {"ncm_code": "8536.41.00", "origin": "0", "icms": 7.0, "ipi": 0.0, "icms_st": 0.0}


def test_compare_fields_flags_only_the_divergent_field() -> None:
    rows = compare_fields(_BASE, {**_BASE, "ncm_code": "8536.49.00"})

    diverging = {row["name"]: row for row in rows if row["diverges"]}
    assert list(diverging) == ["NCM"]
    assert diverging["NCM"]["declared"] == "8536.41.00"
    assert diverging["NCM"]["correct"] == "8536.49.00"


def test_percentage_fields_compare_numerically() -> None:
    rows = compare_fields({**_BASE, "icms": "18"}, {**_BASE, "icms": 18.0})

    assert not any(row["diverges"] for row in rows)


def test_none_on_both_sides_is_not_a_divergence() -> None:
    empty = {"ncm_code": None, "origin": None, "icms": None, "ipi": None, "icms_st": None}

    assert not any(row["diverges"] for row in compare_fields(empty, empty))


def test_none_on_one_side_only_is_a_divergence() -> None:
    rows = compare_fields({**_BASE, "origin": None}, _BASE)

    assert [row["name"] for row in rows if row["diverges"]] == ["Origem"]


@pytest.mark.asyncio
async def test_use_case_returns_one_entry_per_item_with_all_fields() -> None:
    use_case = GetOrderTaxComparisonUseCase(
        FakeRepository([_item(_BASE, {**_BASE, "ipi": 3.25})])
    )

    result = await use_case.execute(4513484862)

    assert len(result) == 1
    assert result[0]["part_number"] == "EF04066"
    assert len(result[0]["fields"]) == 5
    assert [f["name"] for f in result[0]["fields"] if f["diverges"]] == ["IPI"]


@pytest.mark.asyncio
async def test_use_case_returns_empty_list_when_no_reference_exists() -> None:
    assert await GetOrderTaxComparisonUseCase(FakeRepository([])).execute(1) == []


@pytest.mark.asyncio
async def test_use_case_exposes_ticket_state_and_snapshot_source() -> None:
    item = _item(_BASE, {**_BASE, "ncm_code": "8536.49.00"})
    item.update(
        declared_source="snapshot",
        state="resolvida",
        ticket={"id": 1005, "number": 364947, "opened_at": None, "closed_at": None},
    )

    result = await GetOrderTaxComparisonUseCase(FakeRepository([item])).execute(1)

    assert result[0]["state"] == "resolvida"
    assert result[0]["declared_source"] == "snapshot"
    assert result[0]["ticket"]["number"] == 364947


@pytest.mark.asyncio
async def test_use_case_defaults_to_open_and_live_when_repository_omits_them() -> None:
    result = await GetOrderTaxComparisonUseCase(
        FakeRepository([_item(_BASE, _BASE)])
    ).execute(1)

    assert result[0]["state"] == "aberta"
    assert result[0]["declared_source"] == "live"
    assert result[0]["ticket"] is None
