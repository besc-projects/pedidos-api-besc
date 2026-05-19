from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tickets import Ticket
from app.models.tickets import TicketProgress
from app.schemas.ticket.progress import (
    TicketProgressCreate,
    TicketProgressResponse,
    TicketProgressUpdate,
)
from sqlalchemy import and_


async def create_ticket_progress(
    db: AsyncSession, ticket_id: int, progress_in: TicketProgressCreate
) -> TicketProgressResponse:
    ticket = await db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    progress = TicketProgress(ticket_id=ticket_id, **progress_in.model_dump())
    db.add(progress)
    await db.commit()
    await db.refresh(progress)
    return TicketProgressResponse.model_validate(progress, from_attributes=True)


async def get_ticket_progresses(db: AsyncSession, ticket_id: int) -> list[TicketProgressResponse]:
    result = await db.execute(
        select(TicketProgress).where(TicketProgress.ticket_id == ticket_id)
    )
    progresses = result.scalars().all()
    return [
        TicketProgressResponse.model_validate(progress, from_attributes=True)
        for progress in progresses
    ]


async def update_ticket_progress(
    db: AsyncSession,
    ticket_id: int,
    progress_id: str,
    progress_in: TicketProgressUpdate,
) -> TicketProgressResponse:
    result = await db.execute(
        select(TicketProgress).where(
            TicketProgress.id == progress_id,
            TicketProgress.ticket_id == ticket_id,
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progress not found")

    update_data = progress_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(progress, field, value)

    await db.commit()
    await db.refresh(progress)
    return TicketProgressResponse.model_validate(progress, from_attributes=True)





async def delete_ticket_progress_all(db: AsyncSession, ticket_id: int) -> dict:
    result = await db.execute(
        delete(TicketProgress).where(TicketProgress.ticket_id == ticket_id)
    )
    deleted_count = result.rowcount or 0

    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )

    await db.commit()
    return {
        "message": "Progress deleted successfully",
        "deleted_count": deleted_count,
    }


async def delete_ticket_progress(db: AsyncSession, ticket_id: int, progress_id: str) -> dict:
    result = await db.execute(
        select(TicketProgress).where(
            TicketProgress.id == progress_id,
            TicketProgress.ticket_id == ticket_id,
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progress not found")

    await db.delete(progress)
    await db.commit()
    return {"message": "Progress deleted successfully"}
