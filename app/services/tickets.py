from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.tickets import Ticket as TicketModel
from app.models.orders import Order as OrderModel
from app.schemas.tickets import (
    TicketCreate,
    TicketResponse,
    TicketUpdate,
    TicketUpdateResponse,
)


DEFAULT_TICKET_STATUSES = {
    0: ("EM_ABERTO", "Em aberto"),
    1: ("EM_ANDAMENTO", "Em andamento"),
    2: ("CONCLUIDO", "Concluido"),
    3: ("REABERTO", "Reaberto"),
}


def _status_reaches_filtered(status_id: int | None) -> bool:
    # Status 2 normalmente representa "Concluido" no fluxo de chamados.
    return status_id == 2


async def _ensure_ticket_number_unique(
    db: AsyncSession, ticket_number: int | None, current_id: int | None = None
) -> None:
    if ticket_number is None:
        return

    result = await db.execute(
        select(TicketModel).where(TicketModel.ticket_number == ticket_number)
    )
    existing = result.scalar_one_or_none()
    if existing and existing.id != current_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticket number '{ticket_number}' already exists",
        )


async def _ensure_ticket_status_exists(db: AsyncSession, status_id: int | None) -> None:
    if status_id is None:
        return

    result = await db.execute(
        text("SELECT 1 FROM tickets_status WHERE id = :status_id"),
        {"status_id": status_id},
    )
    if result.scalar_one_or_none() is not None:
        return

    default_status = DEFAULT_TICKET_STATUSES.get(status_id)
    if default_status:
        name, description = default_status

        cols_result = await db.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'tickets_status'
                """
            )
        )
        existing_columns = {row[0] for row in cols_result.fetchall()}

        insert_columns = ["id"]
        insert_params = {"id": status_id}

        if "name" in existing_columns:
            insert_columns.append("name")
            insert_params["name"] = name

        if "description" in existing_columns:
            insert_columns.append("description")
            insert_params["description"] = description

        columns_sql = ", ".join(insert_columns)
        values_sql = ", ".join(f":{col}" for col in insert_columns)

        await db.execute(
            text(
                f"""
                INSERT INTO tickets_status ({columns_sql})
                VALUES ({values_sql})
                ON CONFLICT (id) DO NOTHING
                """
            ),
            insert_params,
        )
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            f"Invalid status_id '{status_id}'. "
            f"Create this status first in tickets_status table."
        ),
    )


# 🟢 Create a ticket
async def create_ticket(db: AsyncSession, ticket_in: TicketCreate) -> TicketResponse:
    """
    Create a new support ticket.
    """
    payload = ticket_in.model_dump()
    await _ensure_ticket_number_unique(db, payload.get("ticket_number"))
    await _ensure_ticket_status_exists(db, payload.get("status_id"))

    db_ticket = TicketModel(**payload)

    order = await db.execute(select(OrderModel).where(OrderModel.vale_order_id == db_ticket.purchase_order))
    order = order.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with purchase order '{payload['purchase_order']}' not found",
        )

    # Associa o ticket ao pedido; múltiplos tickets por purchase_order são permitidos.
    # O ticket_id do pedido sempre refletirá o ticket mais recente.
    db_ticket.order_id = order.id
    db.add(db_ticket)

    try:
        await db.flush()

        order.ticket_id = db_ticket.id

        await db.commit()
        await db.refresh(db_ticket)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while creating ticket: {str(e)}",
        )

    return TicketResponse.model_validate(db_ticket, from_attributes=True)


# 🟡 Get all tickets
async def get_all_tickets(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status_id: int | None = None,
    ticket_number: int | None = None,
    purchase_order: str | None = None,
) -> list[TicketResponse]:
    stmt = select(TicketModel).offset(skip).limit(limit)

    if status_id is not None:
        stmt = stmt.where(TicketModel.status_id == status_id)

    if ticket_number is not None:
        stmt = stmt.where(TicketModel.ticket_number == ticket_number)
         
    if purchase_order:
        stmt = stmt.where(TicketModel.purchase_order == int(purchase_order))

    result = await db.execute(stmt)
    tickets = result.scalars().all()
    return [TicketResponse.model_validate(ticket, from_attributes=True) for ticket in tickets]


# 🔵 Get ticket by ID
async def get_ticket(db: AsyncSession, ticket_number: int) -> TicketResponse:
    """
    Retrieve a single ticket by its ticket number.
    """
    result = await db.execute(select(TicketModel).where(TicketModel.ticket_number == ticket_number))
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return TicketResponse.model_validate(ticket, from_attributes=True)


# 🟠 Update a ticket
async def update_ticket(
    db: AsyncSession, ticket_id: int, ticket_in: TicketUpdate
) -> TicketUpdateResponse:
    """
    Update an existing ticket by its ID.
    """
    result = await db.execute(select(TicketModel).where(TicketModel.id == ticket_id))
    existing_ticket = result.scalar_one_or_none()

    if not existing_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    update_data = ticket_in.model_dump(exclude_unset=True)

    if "ticket_number" in update_data:
        await _ensure_ticket_number_unique(
            db, update_data.get("ticket_number"), current_id=ticket_id
        )

    if "status_id" in update_data:
        await _ensure_ticket_status_exists(db, update_data.get("status_id"))

    changed_fields: list[str] = []
    for field, new_value in update_data.items():
        old_value = getattr(existing_ticket, field)
        if old_value != new_value:
            setattr(existing_ticket, field, new_value)
            changed_fields.append(field)

    if not changed_fields:
        return TicketUpdateResponse(
            message="No changes detected",
            updated_fields=[],
            ticket=TicketResponse.model_validate(existing_ticket, from_attributes=True),
        )

    if "status_id" in changed_fields and "observer_range_date" not in changed_fields:
        if _status_reaches_filtered(existing_ticket.status_id):
            existing_ticket.observer_range_date = datetime.now(timezone.utc).strftime(
                "%Y-%m-%d"
            )
            changed_fields.append("observer_range_date")

    try:
        await db.commit()
        await db.refresh(existing_ticket)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while updating ticket: {str(e)}",
        )

    return TicketUpdateResponse(
        message="Ticket updated successfully",
        updated_fields=changed_fields,
        ticket=TicketResponse.model_validate(existing_ticket, from_attributes=True),
    )


# 🔴 Delete a ticket
async def delete_ticket(db: AsyncSession, ticket_id: int):
    """
    Delete a ticket by its ID.
    """
    result = await db.execute(select(TicketModel).where(TicketModel.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    try:
        await db.execute(delete(TicketModel).where(TicketModel.id == ticket_id))
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while deleting ticket: {str(e)}",
        )

    return {"message": "Ticket successfully deleted"}


