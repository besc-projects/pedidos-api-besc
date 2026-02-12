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
    Permite múltiplos registros para o mesmo pedido e step.
    """
    try:
        # Cria o novo registro
        history = HistoryProcess(**data.model_dump(exclude_none=True))
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
                "detail": str(e),
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
            .order_by(HistoryProcess.occurred_at.desc())
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


async def get_history_by_order_id(db: AsyncSession, order_id: int) -> JSONResponse:
    """
    Retorna todos os registros de histórico para um pedido específico.
    """
    try:
        result = await db.execute(
            select(HistoryProcess)
            .where(HistoryProcess.order_id == order_id)
            .order_by(HistoryProcess.occurred_at.desc())
        )
        histories = result.scalars().all()

        if not histories:
            return JSONResponse(
                status_code=404,
                content={
                    "message": f"Nenhum histórico encontrado para o pedido {order_id}"
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "order_id": order_id,
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


async def get_history_by_step(
    db: AsyncSession, order_id: int, step: str
) -> JSONResponse:
    """
    Retorna todos os registros de histórico para um pedido e step específicos.
    """
    try:
        result = await db.execute(
            select(HistoryProcess)
            .where(
                HistoryProcess.order_id == order_id,
                HistoryProcess.step == step,
            )
            .order_by(HistoryProcess.occurred_at.desc())
        )
        histories = result.scalars().all()

        if not histories:
            return JSONResponse(
                status_code=404,
                content={
                    "message": f"Nenhum histórico encontrado para order_id {order_id} e step '{step}'"
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "order_id": order_id,
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
