from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.history_process.use_cases import (
    CreateHistoryProcessUseCase,
    ListHistoryProcessByOrderUseCase,
    ListHistoryProcessByStepUseCase,
    ListHistoryProcessUseCase,
)
from app.database import get_db
from app.domain.protocols.history_process_repository import (
    HistoryProcessRepositoryProtocol,
)
from app.infrastructure.repositories.history_process_repository import (
    SqlAlchemyHistoryProcessRepository,
)


def get_history_process_repository(
    db: AsyncSession = Depends(get_db),
) -> HistoryProcessRepositoryProtocol:
    return SqlAlchemyHistoryProcessRepository(db)


def get_create_history_process_use_case(
    repository: HistoryProcessRepositoryProtocol = Depends(
        get_history_process_repository
    ),
) -> CreateHistoryProcessUseCase:
    return CreateHistoryProcessUseCase(repository)


def get_list_history_process_use_case(
    repository: HistoryProcessRepositoryProtocol = Depends(
        get_history_process_repository
    ),
) -> ListHistoryProcessUseCase:
    return ListHistoryProcessUseCase(repository)


def get_list_history_process_by_order_use_case(
    repository: HistoryProcessRepositoryProtocol = Depends(
        get_history_process_repository
    ),
) -> ListHistoryProcessByOrderUseCase:
    return ListHistoryProcessByOrderUseCase(repository)


def get_list_history_process_by_step_use_case(
    repository: HistoryProcessRepositoryProtocol = Depends(
        get_history_process_repository
    ),
) -> ListHistoryProcessByStepUseCase:
    return ListHistoryProcessByStepUseCase(repository)
