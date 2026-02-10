from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.history_process import (
    create_history_process,
    get_all_history,
    get_history_by_orders,
    get_history_by_step,
)
from app.schemas.history_process import (
    HistoryProcessCreate,
    HistoryProcessResponse,
    HistoryProcessListResponse,
)

router = APIRouter(prefix="/api/history-process")


@router.post("/", status_code=201)
async def create(data: HistoryProcessCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria um novo registro de histórico de processo.

    **Regras:**
    - `id_situation` deve ser maior que 0
    - Não pode existir o mesmo `id_situation` para o mesmo `step` na mesma `orders`

    **Exemplo:**
    - ✅ Permitido: orders='123', step='proposta', id_situation=1
    - ❌ Bloqueado: orders='123', step='proposta', id_situation=1 (duplicado)
    - ✅ Permitido: orders='123', step='proposta', id_situation=2
    """
    return await create_history_process(db, data)


@router.get("/", response_model=HistoryProcessListResponse)
async def get_all(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(
        100, ge=1, le=1000, description="Número máximo de registros a retornar"
    ),
):
    """
    Retorna todos os registros de histórico com paginação.
    """
    return await get_all_history(db, skip, limit)


@router.get("/orders/{orders}")
async def get_by_orders(orders: str, db: AsyncSession = Depends(get_db)):
    """
    Retorna todos os registros de histórico para um pedido específico.
    """
    return await get_history_by_orders(db, orders)


@router.get("/orders/{orders}/step/{step}")
async def get_by_step(orders: str, step: str, db: AsyncSession = Depends(get_db)):
    """
    Retorna todos os registros de histórico para um pedido e step específicos.
    """
    return await get_history_by_step(db, orders, step)
