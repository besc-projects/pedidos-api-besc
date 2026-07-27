from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.dependencies.history_process import (
    get_create_history_process_use_case,
    get_list_history_process_by_order_use_case,
    get_list_history_process_by_step_use_case,
    get_list_history_process_use_case,
)
from app.application.use_cases.history_process.use_cases import (
    CreateHistoryProcessUseCase,
    ListHistoryProcessByOrderUseCase,
    ListHistoryProcessByStepUseCase,
    ListHistoryProcessUseCase,
)
from app.schemas.history_process import (
    HistoryProcessCreate,
    HistoryProcessListResponse,
    HistoryProcessResponse,
)

router = APIRouter(prefix="/api/history-process", tags=["History Process"])


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a history event")
async def create(
    data: HistoryProcessCreate,
    use_case: CreateHistoryProcessUseCase = Depends(
        get_create_history_process_use_case
    ),
) -> JSONResponse:
    entry = await use_case.execute(data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "History created successfully.",
            "data": jsonable_encoder(
                HistoryProcessResponse.model_validate(entry, from_attributes=True)
            ),
        },
    )


@router.get(
    "/",
    response_model=HistoryProcessListResponse,
    summary="List history events (paginated)",
)
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    use_case: ListHistoryProcessUseCase = Depends(get_list_history_process_use_case),
) -> HistoryProcessListResponse:
    total, items = await use_case.execute(skip, limit)
    return HistoryProcessListResponse(
        total=total,
        items=[
            HistoryProcessResponse.model_validate(item, from_attributes=True)
            for item in items
        ],
    )


@router.get("/order/{order_id}", summary="List history events for an order")
async def get_by_order(
    order_id: int,
    use_case: ListHistoryProcessByOrderUseCase = Depends(
        get_list_history_process_by_order_use_case
    ),
) -> JSONResponse:
    items = await use_case.execute(order_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            {
                "order_id": order_id,
                "total": len(items),
                "items": [
                    HistoryProcessResponse.model_validate(item, from_attributes=True)
                    for item in items
                ],
            }
        ),
    )


@router.get(
    "/order/{order_id}/step/{step}",
    summary="List history events for an order and step",
)
async def get_by_step(
    order_id: int,
    step: str,
    use_case: ListHistoryProcessByStepUseCase = Depends(
        get_list_history_process_by_step_use_case
    ),
) -> JSONResponse:
    items = await use_case.execute(order_id, step)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            {
                "order_id": order_id,
                "step": step,
                "total": len(items),
                "items": [
                    HistoryProcessResponse.model_validate(item, from_attributes=True)
                    for item in items
                ],
            }
        ),
    )
