from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.ticket_progresses.use_cases import (
    CreateTicketProgressUseCase,
    DeleteAllTicketProgressesUseCase,
    ListTicketProgressesUseCase,
    UpdateTicketProgressUseCase,
)
from app.database import get_db
from app.domain.protocols.ticket_progress_repository import (
    TicketProgressRepositoryProtocol,
)
from app.infrastructure.repositories.ticket_progress_repository import (
    SqlAlchemyTicketProgressRepository,
)


def get_ticket_progress_repository(
    db: AsyncSession = Depends(get_db),
) -> TicketProgressRepositoryProtocol:
    return SqlAlchemyTicketProgressRepository(db)


def get_create_ticket_progress_use_case(
    repository: TicketProgressRepositoryProtocol = Depends(
        get_ticket_progress_repository
    ),
) -> CreateTicketProgressUseCase:
    return CreateTicketProgressUseCase(repository)


def get_list_ticket_progresses_use_case(
    repository: TicketProgressRepositoryProtocol = Depends(
        get_ticket_progress_repository
    ),
) -> ListTicketProgressesUseCase:
    return ListTicketProgressesUseCase(repository)


def get_update_ticket_progress_use_case(
    repository: TicketProgressRepositoryProtocol = Depends(
        get_ticket_progress_repository
    ),
) -> UpdateTicketProgressUseCase:
    return UpdateTicketProgressUseCase(repository)


def get_delete_all_ticket_progresses_use_case(
    repository: TicketProgressRepositoryProtocol = Depends(
        get_ticket_progress_repository
    ),
) -> DeleteAllTicketProgressesUseCase:
    return DeleteAllTicketProgressesUseCase(repository)
