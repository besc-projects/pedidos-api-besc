from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tickets import Ticket
from app.models.tickets import TicketDivergence
from app.schemas.ticket.divergence import (
    TicketDivergenceCreate,
    TicketDivergenceResponse,
    TicketDivergenceUpdate,
)


async def create_ticket_divergence(
    db: AsyncSession,
    ticket_id: int,
    divergence_in: TicketDivergenceCreate,
) -> TicketDivergenceResponse:
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    result = await db.execute(
        select(TicketDivergence).where(
            TicketDivergence.purchase_order_line == divergence_in.purchase_order_line,
            TicketDivergence.item_id == divergence_in.item_id,
        )
    )


    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Divergence '{divergence_in.purchase_order_line}/{divergence_in.item_id}' already exists"
            ),
        )

    divergence = TicketDivergence(
        ticket_id=ticket_id,
        **divergence_in.model_dump(),
    )
    db.add(divergence)
    await db.commit()
    await db.refresh(divergence)
    return TicketDivergenceResponse.model_validate(divergence, from_attributes=True)


async def get_ticket_divergences(
    db: AsyncSession, ticket_id: int
) -> list[TicketDivergenceResponse]:
    result = await db.execute(
        select(TicketDivergence).where(TicketDivergence.ticket_id == ticket_id)
    )
    divergences = result.scalars().all()
    return [
        TicketDivergenceResponse.model_validate(divergence, from_attributes=True)
        for divergence in divergences
    ]


async def update_ticket_divergence(
    db: AsyncSession,
    ticket_id: int,
    purchase_order_line: int,
    item_id: int,
    divergence_in: TicketDivergenceUpdate,
) -> TicketDivergenceResponse:
    result = await db.execute(
        select(TicketDivergence).where(
            TicketDivergence.purchase_order_line == purchase_order_line,
            TicketDivergence.item_id == item_id,
            TicketDivergence.ticket_id == ticket_id,
        )
    )
    divergence = result.scalar_one_or_none()

    if not divergence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Divergence not found",
        )

    update_data = divergence_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(divergence, field, value)

    await db.commit()
    await db.refresh(divergence)
    return TicketDivergenceResponse.model_validate(divergence, from_attributes=True)


async def delete_ticket_divergence(
    db: AsyncSession,
    ticket_id: int,
    purchase_order_line: int,
    item_id: int,
) -> dict:
    result = await db.execute(
        select(TicketDivergence).where(
            TicketDivergence.purchase_order_line == purchase_order_line,
            TicketDivergence.item_id == item_id,
            TicketDivergence.ticket_id == ticket_id,
        )
    )
    divergence = result.scalar_one_or_none()

    if not divergence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Divergence not found",
        )

    await db.delete(divergence)
    await db.commit()
    return {"message": "Divergence deleted successfully"}
