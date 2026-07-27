from fastapi import APIRouter, Depends, status

from app.api.dependencies.ticket_divergences import (
    get_create_ticket_divergence_use_case,
    get_delete_ticket_divergence_use_case,
    get_list_ticket_divergences_use_case,
    get_update_ticket_divergence_use_case,
)
from app.application.use_cases.ticket_divergences.use_cases import (
    CreateTicketDivergenceUseCase,
    DeleteTicketDivergenceUseCase,
    ListTicketDivergencesUseCase,
    UpdateTicketDivergenceUseCase,
)
from app.schemas.ticket.divergence import (
    TicketDivergenceCreate,
    TicketDivergenceResponse,
    TicketDivergenceUpdate,
)

router = APIRouter(prefix="/api/{ticket_id}/divergences", tags=["Ticket Divergences"])


@router.get("/", response_model=list[TicketDivergenceResponse])
async def list_divergences(
    ticket_id: int,
    use_case: ListTicketDivergencesUseCase = Depends(
        get_list_ticket_divergences_use_case
    ),
) -> list[TicketDivergenceResponse]:
    return await use_case.execute(ticket_id)


@router.post(
    "/",
    response_model=TicketDivergenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_divergence(
    ticket_id: int,
    divergence_in: TicketDivergenceCreate,
    use_case: CreateTicketDivergenceUseCase = Depends(
        get_create_ticket_divergence_use_case
    ),
) -> TicketDivergenceResponse:
    return await use_case.execute(ticket_id, divergence_in)


@router.patch(
    "/{divergence_id}/{item_id}",
    response_model=TicketDivergenceResponse,
)
async def patch_divergence(
    ticket_id: int,
    divergence_id: int,
    item_id: int,
    divergence_in: TicketDivergenceUpdate,
    use_case: UpdateTicketDivergenceUseCase = Depends(
        get_update_ticket_divergence_use_case
    ),
) -> TicketDivergenceResponse:
    return await use_case.execute(ticket_id, divergence_id, item_id, divergence_in)


@router.delete("/{divergence_id}/{item_id}")
async def remove_divergence(
    ticket_id: int,
    divergence_id: int,
    item_id: int,
    use_case: DeleteTicketDivergenceUseCase = Depends(
        get_delete_ticket_divergence_use_case
    ),
) -> dict:
    await use_case.execute(ticket_id, divergence_id, item_id)
    return {"message": "Divergence deleted successfully"}
