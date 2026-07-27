from app.domain.entities.history_process_entry import HistoryProcessEntry
from app.domain.exceptions import ConflictException, NotFoundException
from app.domain.protocols.history_process_repository import (
    HistoryProcessRepositoryProtocol,
)
from app.schemas.history_process import HistoryProcessCreate


class CreateHistoryProcessUseCase:
    """Create a history event, avoiding duplicates per (order_id, description)."""

    def __init__(self, repository: HistoryProcessRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: HistoryProcessCreate) -> HistoryProcessEntry:
        existing = await self._repository.get_by_order_and_description(
            data.order_id, data.description
        )
        if existing is not None:
            raise ConflictException(
                "This history already exists for this order "
                f"(order_id={data.order_id})."
            )

        entry = HistoryProcessEntry(
            order_id=data.order_id,
            step=data.step,
            description=data.description,
            severity=data.severity.value,
            created_by=data.created_by,
            occurred_at=data.occurred_at,
        )
        return await self._repository.create(entry)


class ListHistoryProcessUseCase:
    """List history events with pagination and a total count."""

    def __init__(self, repository: HistoryProcessRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, skip: int, limit: int
    ) -> tuple[int, list[HistoryProcessEntry]]:
        total = await self._repository.count()
        items = await self._repository.list(skip, limit)
        return total, items


class ListHistoryProcessByOrderUseCase:
    """List history events for an order."""

    def __init__(self, repository: HistoryProcessRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, order_id: int) -> list[HistoryProcessEntry]:
        items = await self._repository.list_by_order(order_id)
        if not items:
            raise NotFoundException(
                f"No history found for order {order_id}."
            )
        return items


class ListHistoryProcessByStepUseCase:
    """List history events for an order and step."""

    def __init__(self, repository: HistoryProcessRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, order_id: int, step: str) -> list[HistoryProcessEntry]:
        items = await self._repository.list_by_step(order_id, step)
        if not items:
            raise NotFoundException(
                f"No history found for order {order_id} and step '{step}'."
            )
        return items
