from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from typing import List

from app.models.tax_reference import TaxReferenceProductSupra as TaxReferenceModel
from app.schemas.tax_reference import (
    TaxReferenceCreate,
    TaxReferenceUpdate,
    TaxReferenceResponse,
)


# 🟢 Create
async def create_tax_reference(
    db: AsyncSession, data: TaxReferenceCreate
) -> TaxReferenceResponse:
    """Cria uma nova referência fiscal de produto supra."""
    new_entry = TaxReferenceModel(**data.model_dump())
    db.add(new_entry)

    try:
        await db.commit()
        await db.refresh(new_entry)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar referência fiscal: {str(e)}",
        )

    return TaxReferenceResponse.model_validate(new_entry, from_attributes=True)


# 🔵 Get by ID
async def get_tax_reference_by_id(
    db: AsyncSession, entry_id: int
) -> TaxReferenceResponse:
    """Retorna uma referência fiscal pelo ID do registro."""
    result = await db.execute(
        select(TaxReferenceModel).where(TaxReferenceModel.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"Referência fiscal com ID {entry_id} não encontrada",
        )

    return TaxReferenceResponse.model_validate(entry, from_attributes=True)


# 🔵 Get by id_product
async def get_tax_reference_by_product(
    db: AsyncSession, id_product: int
) -> List[TaxReferenceResponse]:
    """Retorna todas as referências fiscais de um produto pelo id_product."""
    result = await db.execute(
        select(TaxReferenceModel).where(TaxReferenceModel.id_product == id_product)
    )
    entries = result.scalars().all()

    if not entries:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhuma referência fiscal encontrada para o produto {id_product}",
        )

    return [
        TaxReferenceResponse.model_validate(e, from_attributes=True) for e in entries
    ]


# 🟡 Get all
async def get_all_tax_references(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[TaxReferenceResponse]:
    """Retorna todas as referências fiscais com paginação."""
    result = await db.execute(select(TaxReferenceModel).offset(skip).limit(limit))
    entries = result.scalars().all()

    return [
        TaxReferenceResponse.model_validate(e, from_attributes=True) for e in entries
    ]


# 🟠 Update
async def update_tax_reference(
    db: AsyncSession, entry_id: int, data: TaxReferenceUpdate
) -> TaxReferenceResponse:
    """Atualiza qualquer campo de uma referência fiscal pelo ID do registro."""
    result = await db.execute(
        select(TaxReferenceModel).where(TaxReferenceModel.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"Referência fiscal com ID {entry_id} não encontrada",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    try:
        await db.commit()
        await db.refresh(entry)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar referência fiscal: {str(e)}",
        )

    return TaxReferenceResponse.model_validate(entry, from_attributes=True)


# 🔴 Delete
async def delete_tax_reference(db: AsyncSession, entry_id: int) -> dict:
    """Remove uma referência fiscal pelo ID do registro."""
    result = await db.execute(
        select(TaxReferenceModel).where(TaxReferenceModel.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"Referência fiscal com ID {entry_id} não encontrada",
        )

    try:
        await db.delete(entry)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar referência fiscal: {str(e)}",
        )

    return {"detail": f"Referência fiscal com ID {entry_id} deletada com sucesso"}
