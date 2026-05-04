from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.tax_reference import (
    TaxReferenceCreate,
    TaxReferenceUpdate,
    TaxReferenceResponse,
)
from app.services.tax_reference import (
    create_tax_reference,
    get_tax_reference_by_id,
    get_tax_reference_by_product,
    get_all_tax_references,
    update_tax_reference,
    delete_tax_reference,
)

router = APIRouter(prefix="/api/tax-reference", tags=["Tax Reference"])


# 🟢 Create
@router.post(
    "/",
    response_model=TaxReferenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar referência fiscal de produto supra",
)
async def create_entry(data: TaxReferenceCreate, db: AsyncSession = Depends(get_db)):
    return await create_tax_reference(db, data)


# 🔵 Get by id_product
@router.get(
    "/product/{id_product}",
    response_model=List[TaxReferenceResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar referências fiscais por id_product",
)
async def get_by_product(id_product: int, db: AsyncSession = Depends(get_db)):
    return await get_tax_reference_by_product(db, id_product)


# 🟡 Get all
@router.get(
    "/",
    response_model=List[TaxReferenceResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todas as referências fiscais",
)
async def get_all(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_all_tax_references(db, skip, limit)


# 🟣 Get by ID
@router.get(
    "/{entry_id}",
    response_model=TaxReferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar referência fiscal por ID",
)
async def get_by_id(entry_id: int, db: AsyncSession = Depends(get_db)):
    return await get_tax_reference_by_id(db, entry_id)


# 🟠 Update
@router.patch(
    "/{entry_id}",
    response_model=TaxReferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar referência fiscal",
    description="Atualiza qualquer campo da referência fiscal. Apenas os campos enviados serão alterados.",
)
async def update_entry(
    entry_id: int, data: TaxReferenceUpdate, db: AsyncSession = Depends(get_db)
):
    return await update_tax_reference(db, entry_id, data)


# 🔴 Delete
@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_200_OK,
    summary="Deletar referência fiscal",
)
async def delete_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_tax_reference(db, entry_id)
