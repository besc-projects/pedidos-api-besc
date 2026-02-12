from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.history_process import (
    create_history_process,
    get_all_history,
    get_history_by_order_id,
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

    **Campos:**
    - `order_id`: ID do pedido (obrigatório, BigInteger)
    - `step`: Etapa do processo (obrigatório, até 80 caracteres)
    - `description`: Descrição detalhada do evento (obrigatório)
    - `severity`: Severidade do evento - info|warning|error (opcional, padrão: info)
    - `created_by`: Email/login/nome do criador (opcional, até 120 caracteres)
    - `occurred_at`: Quando o evento ocorreu (opcional, padrão: agora)

    **Exemplo:**
    ```json
    {
      "order_id": 123,
      "step": "cadastro",
      "description": "Pedido criado com sucesso",
      "severity": "info",
      "created_by": "usuario@email.com"
    }
    ```
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
    Ordenado por occurred_at (mais recente primeiro).
    """
    return await get_all_history(db, skip, limit)


@router.get("/order/{order_id}")
async def get_by_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna todos os registros de histórico para um pedido específico.
    Ordenado por occurred_at (mais recente primeiro).
    """
    return await get_history_by_order_id(db, order_id)


@router.get("/order/{order_id}/step/{step}")
async def get_by_step(order_id: int, step: str, db: AsyncSession = Depends(get_db)):
    """
    Retorna todos os registros de histórico para um pedido e step específicos.
    Ordenado por occurred_at (mais recente primeiro).
    """
    return await get_history_by_step(db, order_id, step)
