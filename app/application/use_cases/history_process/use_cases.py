from datetime import date

from sqlalchemy.exc import IntegrityError

from app.domain.entities.history_process_entry import HistoryProcessEntry
from app.domain.exceptions import ConflictException, NotFoundException
from app.domain.protocols.history_process_repository import (
    HistoryProcessRepositoryProtocol,
)
from app.schemas.history_process import HistoryProcessCreate


class CreateHistoryProcessUseCase:
    """Create a history event, avoiding duplicates per (order_id, description).

    A dedup em si é o índice único ``uq_audit_process_history_order_description``
    no banco — insere direto e trata a violação de unicidade como 409. Antes
    disso fazia um SELECT de verificação antes do INSERT (check-then-insert),
    que virou table scan conforme a tabela cresceu e, sob escrita concorrente
    de vários robôs, tendia a lock de tabela (achado de 17/09/2026).
    """

    def __init__(self, repository: HistoryProcessRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: HistoryProcessCreate) -> HistoryProcessEntry:
        entry = HistoryProcessEntry(
            order_id=data.order_id,
            step=data.step,
            description=data.description,
            severity=data.severity.value,
            created_by=data.created_by,
            occurred_at=data.occurred_at,
        )
        try:
            return await self._repository.create(entry)
        except IntegrityError as exc:
            raise ConflictException(
                "This history already exists for this order "
                f"(order_id={data.order_id})."
            ) from exc


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


class ListHistoryProcessByStepAndDateUseCase:
    """List history events of a step across ALL orders, on a given day.

    Para digests (ex.: comercial-report perguntando "quais pedidos
    avançaram de status hoje") — diferente de ListHistoryProcessByStepUseCase,
    que exige um order_id conhecido de antemão. Lista vazia é o caso normal
    (nada aconteceu naquele dia), não um erro — quem chama decide o que
    fazer, sem 404.
    """

    def __init__(self, repository: HistoryProcessRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, step: str, day: date) -> list[HistoryProcessEntry]:
        return await self._repository.list_by_step_and_date(step, day)
