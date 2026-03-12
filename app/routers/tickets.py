from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.tickets import (
    TicketCreate,
    TicketResponse,
    TicketUpdate,
    TicketUpdateResponse,
)
from app.services.tickets import (
    create_ticket,
    get_all_tickets,
    get_ticket,
    update_ticket,
    delete_ticket,
)
from app.routers.ticket.progress import router as progress_router
from app.routers.ticket.divergence import router as divergence_router



router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

router.include_router(progress_router)
router.include_router(divergence_router)



@router.get("/", response_model=list[TicketResponse], status_code=status.HTTP_200_OK)
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_id: int | None = Query(None),
    ticket_number: int | None = Query(None),
    purchase_order: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Traz os chamados com filtros opcionais."""
    return await get_all_tickets(
        db,
        skip=skip,
        limit=limit,
        status_id=status_id,
        ticket_number=ticket_number,
        purchase_order=purchase_order,
    )


@router.get("/{ticket_number}", response_model=TicketResponse, status_code=status.HTTP_200_OK)
async def get_ticket_by_number(ticket_number: int, db: AsyncSession = Depends(get_db)):
    """Busca um chamado por número de ticket."""
    return await get_ticket(db, ticket_number)


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket_route(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
):
    """Cria um novo chamado."""
    return await create_ticket(db, ticket_data)


@router.patch(
    "/{ticket_id}",
    response_model=TicketUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_ticket_route(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Atualiza um chamado e retorna os campos alterados."""
    return await update_ticket(db, ticket_id, ticket_data)


@router.delete("/{ticket_id}", status_code=status.HTTP_200_OK)
async def delete_ticket_route(ticket_id: int, db: AsyncSession = Depends(get_db)):
    """Remove um chamado por ID."""
    return await delete_ticket(db, ticket_id)
