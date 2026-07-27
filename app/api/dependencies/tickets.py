from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.tickets.use_cases import (
    CreateTicketUseCase,
    DeleteTicketUseCase,
    GetTicketUseCase,
    ListTicketsUseCase,
    UpdateTicketUseCase,
)
from app.database import get_db
from app.domain.protocols.ticket_repository import TicketRepositoryProtocol
from app.infrastructure.repositories.ticket_repository import (
    SqlAlchemyTicketRepository,
)


def get_ticket_repository(
    db: AsyncSession = Depends(get_db),
) -> TicketRepositoryProtocol:
    return SqlAlchemyTicketRepository(db)


def get_create_ticket_use_case(
    repository: TicketRepositoryProtocol = Depends(get_ticket_repository),
) -> CreateTicketUseCase:
    return CreateTicketUseCase(repository)


def get_list_tickets_use_case(
    repository: TicketRepositoryProtocol = Depends(get_ticket_repository),
) -> ListTicketsUseCase:
    return ListTicketsUseCase(repository)


def get_get_ticket_use_case(
    repository: TicketRepositoryProtocol = Depends(get_ticket_repository),
) -> GetTicketUseCase:
    return GetTicketUseCase(repository)


def get_update_ticket_use_case(
    repository: TicketRepositoryProtocol = Depends(get_ticket_repository),
) -> UpdateTicketUseCase:
    return UpdateTicketUseCase(repository)


def get_delete_ticket_use_case(
    repository: TicketRepositoryProtocol = Depends(get_ticket_repository),
) -> DeleteTicketUseCase:
    return DeleteTicketUseCase(repository)
