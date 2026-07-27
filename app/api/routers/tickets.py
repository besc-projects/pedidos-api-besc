from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.ticket_divergences import get_divergence_item_ids_use_case
from app.api.dependencies.tickets import (
    get_create_ticket_use_case,
    get_delete_ticket_use_case,
    get_get_ticket_use_case,
    get_list_tickets_use_case,
    get_update_ticket_use_case,
)
from app.api.routers.ticket_divergences import router as divergence_router
from app.api.routers.ticket_progresses import router as progress_router
from app.application.use_cases.ticket_divergences.use_cases import (
    GetDivergenceItemIdsByTicketNumberUseCase,
)
from app.application.use_cases.tickets.use_cases import (
    CreateTicketUseCase,
    DeleteTicketUseCase,
    GetTicketUseCase,
    ListTicketsUseCase,
    UpdateTicketUseCase,
)
from app.schemas.ticket.base import (
    TicketCreate,
    TicketResponse,
    TicketUpdate,
    TicketUpdateResponse,
)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

router.include_router(progress_router)
router.include_router(divergence_router)


@router.get("/", response_model=list[TicketResponse])
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_id: int | None = Query(None),
    ticket_number: int | None = Query(None),
    purchase_order: int | None = Query(None),
    use_case: ListTicketsUseCase = Depends(get_list_tickets_use_case),
) -> list[TicketResponse]:
    return await use_case.execute(
        skip=skip,
        limit=limit,
        status_id=status_id,
        ticket_number=ticket_number,
        purchase_order=purchase_order,
    )


@router.get("/{ticket_number}", response_model=TicketResponse)
async def get_ticket_by_number(
    ticket_number: int,
    use_case: GetTicketUseCase = Depends(get_get_ticket_use_case),
) -> TicketResponse:
    return await use_case.execute(ticket_number)


@router.get("/{ticket_number}/divergences/items", response_model=list[int])
async def list_ticket_divergence_item_ids(
    ticket_number: int,
    use_case: GetDivergenceItemIdsByTicketNumberUseCase = Depends(
        get_divergence_item_ids_use_case
    ),
) -> list[int]:
    return await use_case.execute(ticket_number)


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    use_case: CreateTicketUseCase = Depends(get_create_ticket_use_case),
) -> TicketResponse:
    return await use_case.execute(ticket_data)


@router.patch("/{ticket_id}", response_model=TicketUpdateResponse)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    use_case: UpdateTicketUseCase = Depends(get_update_ticket_use_case),
) -> TicketUpdateResponse:
    message, updated_fields, ticket = await use_case.execute(ticket_id, ticket_data)
    return TicketUpdateResponse(
        message=message,
        updated_fields=updated_fields,
        ticket=TicketResponse.model_validate(ticket, from_attributes=True),
    )


@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    use_case: DeleteTicketUseCase = Depends(get_delete_ticket_use_case),
) -> dict:
    await use_case.execute(ticket_id)
    return {"message": "Ticket successfully deleted"}
