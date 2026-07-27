from fastapi import APIRouter, Depends, status

from app.api.dependencies.ticket_progresses import (
    get_create_ticket_progress_use_case,
    get_delete_all_ticket_progresses_use_case,
    get_list_ticket_progresses_use_case,
    get_update_ticket_progress_use_case,
)
from app.application.use_cases.ticket_progresses.use_cases import (
    CreateTicketProgressUseCase,
    DeleteAllTicketProgressesUseCase,
    ListTicketProgressesUseCase,
    UpdateTicketProgressUseCase,
)
from app.schemas.ticket.progress import (
    TicketProgressCreate,
    TicketProgressResponse,
    TicketProgressUpdate,
)

router = APIRouter(prefix="/api/{ticket_id}/progresses", tags=["Ticket Progresses"])


@router.get("/", response_model=list[TicketProgressResponse])
async def list_progresses(
    ticket_id: int,
    use_case: ListTicketProgressesUseCase = Depends(
        get_list_ticket_progresses_use_case
    ),
) -> list[TicketProgressResponse]:
    return await use_case.execute(ticket_id)


@router.post(
    "/",
    response_model=TicketProgressResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_progress(
    ticket_id: int,
    progress_in: TicketProgressCreate,
    use_case: CreateTicketProgressUseCase = Depends(
        get_create_ticket_progress_use_case
    ),
) -> TicketProgressResponse:
    return await use_case.execute(ticket_id, progress_in)


@router.patch("/{progress_id}", response_model=TicketProgressResponse)
async def patch_progress(
    ticket_id: int,
    progress_id: int,
    progress_in: TicketProgressUpdate,
    use_case: UpdateTicketProgressUseCase = Depends(
        get_update_ticket_progress_use_case
    ),
) -> TicketProgressResponse:
    return await use_case.execute(ticket_id, progress_id, progress_in)


@router.delete("/all")
async def remove_progress_all(
    ticket_id: int,
    use_case: DeleteAllTicketProgressesUseCase = Depends(
        get_delete_all_ticket_progresses_use_case
    ),
) -> dict:
    deleted = await use_case.execute(ticket_id)
    return {"message": "Progress deleted successfully", "deleted_count": deleted}
