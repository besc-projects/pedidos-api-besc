from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.ticket.progress import (
    TicketProgressCreate,
    TicketProgressResponse,
    TicketProgressUpdate,
)
from app.services.ticket.progress import (
    create_ticket_progress,
    delete_ticket_progress,
    get_ticket_progresses,
    update_ticket_progress,
    delete_ticket_progress_all
)


router = APIRouter(prefix="/api/{ticket_id}/progresses", tags=["Ticket Progresses"])


@router.get("/", response_model=list[TicketProgressResponse], status_code=status.HTTP_200_OK)
async def list_progresses(ticket_id: int, db: AsyncSession = Depends(get_db)):
    return await get_ticket_progresses(db, ticket_id)


@router.post("/", response_model=TicketProgressResponse, status_code=status.HTTP_201_CREATED)
async def create_progress(
    ticket_id: int,
    progress_in: TicketProgressCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_ticket_progress(db, ticket_id, progress_in)


@router.patch("/{progress_id}", response_model=TicketProgressResponse, status_code=status.HTTP_200_OK)
async def patch_progress(
    ticket_id: int,
    progress_id: str,
    progress_in: TicketProgressUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await update_ticket_progress(db, ticket_id, progress_id, progress_in)




@router.delete("/all", status_code=status.HTTP_200_OK)
async def remove_progress_all(ticket_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_ticket_progress_all(db, ticket_id)


