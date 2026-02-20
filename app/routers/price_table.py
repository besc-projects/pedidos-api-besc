from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.price_table import (
    PriceTableCreate,
    PriceTableResponse,
    PriceByPNResponse,
    PriceTableUpdate,
)
from app.services.price_table import (
    create_price_table_entry,
    get_price_by_pn,
    get_price_table_entry,
    get_all_price_table_entries,
    update_price_table_entry,
    delete_price_table_entry,
    check_pn_exists,
)

router = APIRouter(prefix="/api/price-table", tags=["Price Table"])


# 🟢 Create price table entry
@router.post(
    "/",
    response_model=PriceTableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto na tabela de preços",
    description="Cria um novo produto na tabela de preços. Valida se o PN já existe.",
)
async def create_price_entry(
    price_data: PriceTableCreate, db: AsyncSession = Depends(get_db)
):
    """
    Cria uma nova entrada na tabela de preços.

    - **pn**: Part Number (único)
    - **long_description**: Descrição longa do produto
    - **description**: Descrição do produto
    - **destination**: Destino do produto
    - **unit_price**: Preço unitário (deve ser maior que 0)
    """
    return await create_price_table_entry(db, price_data)


# 🔵 Get price by PN
@router.get(
    "/price/{pn}",
    response_model=PriceByPNResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar preço por PN",
    description="Retorna o preço unitário de um produto com base no Part Number (PN).",
)
async def get_price_for_pn(
    pn: str,
    state: str = Query(..., min_length=2, max_length=2, description="UF do produto"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna o preço unitário de um produto específico.

    - **pn**: Part Number do produto
    - **state**: UF do estado desejado (ex.: MG, PA)
    """
    return await get_price_by_pn(db, pn, state)


# 🟣 Get price table entry by ID
@router.get(
    "/{entry_id}",
    response_model=PriceTableResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar produto por ID",
    description="Retorna todos os dados de um produto na tabela de preços pelo ID.",
)
async def get_entry_by_id(entry_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna uma entrada completa da tabela de preços.

    - **entry_id**: ID do registro na tabela de preços
    """
    return await get_price_table_entry(db, entry_id)


# 🟡 Get all price table entries
@router.get(
    "/",
    response_model=List[PriceTableResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos os produtos",
    description="Retorna todos os produtos da tabela de preços com paginação.",
)
async def get_all_entries(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna todas as entradas da tabela de preços.

    - **skip**: Número de registros a pular (paginação)
    - **limit**: Número máximo de registros a retornar
    """
    return await get_all_price_table_entries(db, skip, limit)


# 🟠 Update price table entry
@router.patch(
    "/{entry_id}",
    response_model=PriceTableResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar produto",
    description="Atualiza os dados de um produto na tabela de preços.",
)
async def update_entry(
    entry_id: int,
    price_data: PriceTableUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Atualiza uma entrada da tabela de preços.

    - **entry_id**: ID do registro a ser atualizado
    - **price_data**: Dados a serem atualizados (apenas campos fornecidos)
    """
    return await update_price_table_entry(db, entry_id, price_data)


# 🔴 Delete price table entry
@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_200_OK,
    summary="Deletar produto",
    description="Remove um produto da tabela de preços.",
)
async def delete_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    """
    Deleta uma entrada da tabela de preços.

    - **entry_id**: ID do registro a ser deletado
    """
    return await delete_price_table_entry(db, entry_id)


# 🔍 Check if PN exists
@router.get(
    "/check/{pn}",
    status_code=status.HTTP_200_OK,
    summary="Verificar se PN existe",
    description="Verifica se um Part Number já está cadastrado na tabela de preços.",
)
async def check_pn(
    pn: str,
    state: str = Query(..., min_length=2, max_length=2, description="UF do produto"),
    db: AsyncSession = Depends(get_db),
):
    """
    Verifica se um PN já existe na tabela de preços.

    - **pn**: Part Number a ser verificado
    - **state**: UF do estado desejado (ex.: MG, PA)
    """
    exists = await check_pn_exists(db, pn, state)
    return {"pn": pn, "state": state.upper(), "exists": exists}
