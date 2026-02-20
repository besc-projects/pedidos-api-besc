from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.price_table import PriceTable as PriceTableModel
from app.schemas.price_table import (
    PriceTableCreate,
    PriceTableResponse,
    PriceByPNResponse,
    PriceTableUpdate,
)
from typing import List


def _normalize_state(state: str) -> str:
    return state.strip().upper()


# 🟢 Create price table entry
async def create_price_table_entry(
    db: AsyncSession, price_data: PriceTableCreate
) -> PriceTableResponse:
    """
    Cria uma nova entrada na tabela de preços.
    Valida se o PN já existe antes de criar.
    """
    normalized_state = _normalize_state(price_data.destination)

    # Verifica se já existe um produto com o mesmo PN no mesmo estado
    result = await db.execute(
        select(PriceTableModel).where(
            PriceTableModel.pn == price_data.pn,
            PriceTableModel.destination == normalized_state,
        )
    )
    existing_product = result.scalar_one_or_none()

    if existing_product:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Product with PN '{price_data.pn}' already exists "
                f"for destination '{normalized_state}'"
            ),
        )

    # Cria o novo produto
    payload = price_data.model_dump()
    payload["destination"] = normalized_state
    new_entry = PriceTableModel(**payload)
    db.add(new_entry)

    try:
        await db.commit()
        await db.refresh(new_entry)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error while saving price table entry: {str(e)}"
        )

    return PriceTableResponse.model_validate(new_entry, from_attributes=True)


# 🔵 Get price by PN
async def get_price_by_pn(db: AsyncSession, pn: str, state: str) -> PriceByPNResponse:
    """
    Retorna o preço unitário de um produto com base no PN.
    """
    normalized_state = _normalize_state(state)
    result = await db.execute(
        select(PriceTableModel).where(
            PriceTableModel.pn == pn,
            PriceTableModel.destination == normalized_state,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with PN '{pn}' not found for destination '{normalized_state}'",
        )

    return PriceByPNResponse(
        pn=product.pn,
        unit_price=product.unit_price,
        description=product.description,
        destination=product.destination,
    )


# 🟣 Get price table entry by ID
async def get_price_table_entry(db: AsyncSession, entry_id: int) -> PriceTableResponse:
    """
    Retorna uma entrada da tabela de preços pelo ID.
    """
    result = await db.execute(
        select(PriceTableModel).where(PriceTableModel.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=404, detail=f"Price table entry with ID {entry_id} not found"
        )

    return PriceTableResponse.model_validate(entry, from_attributes=True)


# 🟡 Get all price table entries
async def get_all_price_table_entries(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[PriceTableResponse]:
    """
    Retorna todas as entradas da tabela de preços com paginação.
    """
    result = await db.execute(select(PriceTableModel).offset(skip).limit(limit))
    entries = result.scalars().all()

    return [
        PriceTableResponse.model_validate(entry, from_attributes=True)
        for entry in entries
    ]


# 🟠 Update price table entry
async def update_price_table_entry(
    db: AsyncSession, entry_id: int, price_data: PriceTableUpdate
) -> PriceTableResponse:
    """
    Atualiza uma entrada da tabela de preços.
    """
    result = await db.execute(
        select(PriceTableModel).where(PriceTableModel.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=404, detail=f"Price table entry with ID {entry_id} not found"
        )

    # Atualiza apenas os campos fornecidos
    update_data = price_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    try:
        await db.commit()
        await db.refresh(entry)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error while updating price table entry: {str(e)}"
        )

    return PriceTableResponse.model_validate(entry, from_attributes=True)


# 🔴 Delete price table entry
async def delete_price_table_entry(db: AsyncSession, entry_id: int) -> dict:
    """
    Deleta uma entrada da tabela de preços.
    """
    result = await db.execute(
        select(PriceTableModel).where(PriceTableModel.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=404, detail=f"Price table entry with ID {entry_id} not found"
        )

    try:
        await db.delete(entry)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error while deleting price table entry: {str(e)}"
        )

    return {"message": f"Price table entry with ID {entry_id} deleted successfully"}


# 🔍 Check if PN exists
async def check_pn_exists(db: AsyncSession, pn: str, state: str) -> bool:
    """
    Verifica se um PN já existe na tabela de preços.
    """
    normalized_state = _normalize_state(state)
    result = await db.execute(
        select(PriceTableModel).where(
            PriceTableModel.pn == pn,
            PriceTableModel.destination == normalized_state,
        )
    )
    return result.scalar_one_or_none() is not None
