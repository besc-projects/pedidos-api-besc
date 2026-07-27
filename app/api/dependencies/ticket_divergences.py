from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.ticket_divergences.use_cases import (
    CreateTicketDivergenceUseCase,
    DeleteTicketDivergenceUseCase,
    GetDivergenceItemIdsByTicketNumberUseCase,
    ListTicketDivergencesUseCase,
    UpdateTicketDivergenceUseCase,
)
from app.database import get_db
from app.domain.protocols.ticket_divergence_repository import (
    TicketDivergenceRepositoryProtocol,
)
from app.infrastructure.repositories.ticket_divergence_repository import (
    SqlAlchemyTicketDivergenceRepository,
)


def get_ticket_divergence_repository(
    db: AsyncSession = Depends(get_db),
) -> TicketDivergenceRepositoryProtocol:
    return SqlAlchemyTicketDivergenceRepository(db)


def get_create_ticket_divergence_use_case(
    repository: TicketDivergenceRepositoryProtocol = Depends(
        get_ticket_divergence_repository
    ),
) -> CreateTicketDivergenceUseCase:
    return CreateTicketDivergenceUseCase(repository)


def get_list_ticket_divergences_use_case(
    repository: TicketDivergenceRepositoryProtocol = Depends(
        get_ticket_divergence_repository
    ),
) -> ListTicketDivergencesUseCase:
    return ListTicketDivergencesUseCase(repository)


def get_divergence_item_ids_use_case(
    repository: TicketDivergenceRepositoryProtocol = Depends(
        get_ticket_divergence_repository
    ),
) -> GetDivergenceItemIdsByTicketNumberUseCase:
    return GetDivergenceItemIdsByTicketNumberUseCase(repository)


def get_update_ticket_divergence_use_case(
    repository: TicketDivergenceRepositoryProtocol = Depends(
        get_ticket_divergence_repository
    ),
) -> UpdateTicketDivergenceUseCase:
    return UpdateTicketDivergenceUseCase(repository)


def get_delete_ticket_divergence_use_case(
    repository: TicketDivergenceRepositoryProtocol = Depends(
        get_ticket_divergence_repository
    ),
) -> DeleteTicketDivergenceUseCase:
    return DeleteTicketDivergenceUseCase(repository)
