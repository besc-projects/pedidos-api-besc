from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.ticket.divergence import (
    TicketDivergenceCreate,
    TicketDivergenceResponse,
    TicketDivergenceUpdate,
)
from app.services.ticket.divergence import (
    create_ticket_divergence,
    delete_ticket_divergence,
    get_ticket_divergences,
    update_ticket_divergence,
)


router = APIRouter(prefix="/api/{ticket_id}/divergences", tags=["Ticket Divergences"])


@router.get("/", response_model=list[TicketDivergenceResponse], status_code=status.HTTP_200_OK)
async def list_divergences(ticket_id: int, db: AsyncSession = Depends(get_db)):
    return await get_ticket_divergences(db, ticket_id)


@router.post("/", response_model=TicketDivergenceResponse, status_code=status.HTTP_201_CREATED)
async def create_divergence(
    ticket_id: int,
    divergence_in: TicketDivergenceCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_ticket_divergence(db, ticket_id, divergence_in)


@router.patch(
    "/{divergence_id}/{item_id}",
    response_model=TicketDivergenceResponse,
    status_code=status.HTTP_200_OK,
)
async def patch_divergence(
    ticket_id: int,
    divergence_id: int,
    item_id: int,
    divergence_in: TicketDivergenceUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await update_ticket_divergence(
        db,
        ticket_id,
        divergence_id,
        item_id,
        divergence_in,
    )


@router.delete("/{divergence_id}/{item_id}", status_code=status.HTTP_200_OK)
async def remove_divergence(
    ticket_id: int,
    divergence_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await delete_ticket_divergence(db, ticket_id, divergence_id, item_id)
