from __future__ import annotations

from typing import Optional, Protocol

from app.domain.entities.history_process_entry import HistoryProcessEntry


class HistoryProcessRepositoryProtocol(Protocol):
    """Persistence contract for process-history events."""

    async def get_by_order_and_description(
        self, order_id: int, description: str
    ) -> Optional[HistoryProcessEntry]:
        ...

    async def count(self) -> int:
        ...

    async def list(self, skip: int, limit: int) -> list[HistoryProcessEntry]:
        ...

    async def list_by_order(self, order_id: int) -> list[HistoryProcessEntry]:
        ...

    async def list_by_step(
        self, order_id: int, step: str
    ) -> list[HistoryProcessEntry]:
        ...

    async def create(self, entry: HistoryProcessEntry) -> HistoryProcessEntry:
        ...
