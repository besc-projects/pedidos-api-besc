from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.history_process import HistoryProcess
from app.schemas.history_process import HistoryProcessCreate


async def create_history_process(
    db: AsyncSession, data: HistoryProcessCreate
) -> JSONResponse:
    """
    Cria um novo registro de histórico de processo.
    Não permite duplicação de id_situation para o mesmo step na mesma orders.
    """
    try:
        # Verifica se já existe a combinação orders + step + id_situation
        result = await db.execute(
            select(HistoryProcess).where(
                HistoryProcess.orders == data.orders,
                HistoryProcess.step == data.step,
                HistoryProcess.id_situation == data.id_situation,
            )
        )
        existing = result.scalars().first()

        if existing:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Registro já existe",
                    "detail": f"Já existe um registro para orders '{data.orders}', step '{data.step}' com id_situation {data.id_situation}",
                },
            )

        # Cria o novo registro
        history = HistoryProcess(**data.model_dump())
        db.add(history)
        await db.commit()
        await db.refresh(history)

        history_data = jsonable_encoder(history)
        return JSONResponse(
            status_code=201,
            content={
                "message": "Histórico criado com sucesso!",
                "data": history_data,
            },
        )

    except IntegrityError as e:
        await db.rollback()
        return JSONResponse(
            status_code=400,
            content={
                "message": "Erro de integridade ao criar histórico",
                "detail": "Já existe um registro com essa combinação de orders, step e id_situation",
            },
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "message": "Erro interno ao criar histórico",
                "error": str(e),
            },
        )


async def get_all_history(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> JSONResponse:
    """
    Retorna todos os registros de histórico com paginação.
    """
    try:
        # Conta o total de registros
        count_result = await db.execute(select(HistoryProcess))
        total = len(count_result.scalars().all())

        # Busca os registros com paginação
        result = await db.execute(
            select(HistoryProcess)
            .order_by(HistoryProcess.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        histories = result.scalars().all()

        return JSONResponse(
            status_code=200,
            content={
                "total": total,
                "items": jsonable_encoder(histories),
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Erro ao buscar históricos",
                "error": str(e),
            },
        )


async def get_history_by_orders(db: AsyncSession, orders: str) -> JSONResponse:
    """
    Retorna todos os registros de histórico para um pedido específico.
    """
    try:
        result = await db.execute(
            select(HistoryProcess)
            .where(HistoryProcess.orders == orders)
            .order_by(HistoryProcess.created_at.desc())
        )
        histories = result.scalars().all()

        if not histories:
            return JSONResponse(
                status_code=404,
                content={
                    "message": f"Nenhum histórico encontrado para o pedido '{orders}'"
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "orders": orders,
                "total": len(histories),
                "items": jsonable_encoder(histories),
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Erro ao buscar histórico",
                "error": str(e),
            },
        )


async def get_history_by_step(db: AsyncSession, orders: str, step: str) -> JSONResponse:
    """
    Retorna todos os registros de histórico para um pedido e step específicos.
    """
    try:
        result = await db.execute(
            select(HistoryProcess)
            .where(
                HistoryProcess.orders == orders,
                HistoryProcess.step == step,
            )
            .order_by(HistoryProcess.created_at.desc())
        )
        histories = result.scalars().all()

        if not histories:
            return JSONResponse(
                status_code=404,
                content={
                    "message": f"Nenhum histórico encontrado para orders '{orders}' e step '{step}'"
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "orders": orders,
                "step": step,
                "total": len(histories),
                "items": jsonable_encoder(histories),
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Erro ao buscar histórico",
                "error": str(e),
            },
        )
