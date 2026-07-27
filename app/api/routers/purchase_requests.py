from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.dependencies.purchase_requests import (
    get_create_purchase_request_use_case,
    get_list_purchase_requests_use_case,
    get_update_purchase_request_use_case,
)
from app.application.use_cases.purchase_requests.create_purchase_request import (
    CreatePurchaseRequestUseCase,
)
from app.application.use_cases.purchase_requests.list_purchase_requests import (
    ListPurchaseRequestsUseCase,
)
from app.application.use_cases.purchase_requests.update_purchase_request import (
    UpdatePurchaseRequestUseCase,
)
from app.domain.enums.purchase_request_status import PurchaseRequestStatus
from app.schemas.purchase_requests import (
    PurchaseRequestCreate,
    PurchaseRequestFilter,
    PurchaseRequestResponse,
    PurchaseRequestUpdate,
)

router = APIRouter(prefix="/api/purchase-requests")


def _serialize(entity) -> dict:
    return jsonable_encoder(
        PurchaseRequestResponse.model_validate(entity, from_attributes=True)
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Register a purchase request",
    description=(
        "Registers a product whose released quantity is lower than the "
        "requested one. Rejects duplicates for the same order and part number."
    ),
    responses={
        201: {"description": "Purchase request created successfully."},
        400: {"description": "Invalid data or purchase not required."},
        409: {"description": "Duplicate order and part number."},
    },
)
async def create_purchase_request(
    data: PurchaseRequestCreate,
    use_case: CreatePurchaseRequestUseCase = Depends(
        get_create_purchase_request_use_case
    ),
) -> JSONResponse:
    entity = await use_case.execute(data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Purchase request created successfully.",
            "purchase_request": _serialize(entity),
        },
    )


@router.get(
    "/",
    summary="List purchase requests by order",
    description=(
        "Returns the purchase requests of an order, optionally filtered by "
        "status (PENDING or COMPLETED)."
    ),
    responses={200: {"description": "Purchase requests retrieved successfully."}},
)
async def list_purchase_requests(
    order_id: int | None = Query(None, alias="orderId"),
    status_filter: PurchaseRequestStatus | None = Query(None, alias="status"),
    use_case: ListPurchaseRequestsUseCase = Depends(
        get_list_purchase_requests_use_case
    ),
) -> JSONResponse:
    filters = PurchaseRequestFilter(order_id=order_id, status=status_filter)
    entities = await use_case.execute(filters)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Purchase requests retrieved successfully.",
            "total": len(entities),
            "purchase_requests": [_serialize(entity) for entity in entities],
        },
    )


@router.put(
    "/{purchase_request_id}",
    summary="Update a purchase request",
    description=(
        "Updates released and/or requested quantities. The status is always "
        "recomputed by the business rule and any client-sent status is ignored."
    ),
    responses={
        200: {"description": "Purchase request updated successfully."},
        400: {"description": "Invalid data or no fields to update."},
        404: {"description": "Purchase request not found."},
    },
)
async def update_purchase_request(
    purchase_request_id: int,
    data: PurchaseRequestUpdate,
    use_case: UpdatePurchaseRequestUseCase = Depends(
        get_update_purchase_request_use_case
    ),
) -> JSONResponse:
    entity = await use_case.execute(purchase_request_id, data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Purchase request updated successfully.",
            "purchase_request": _serialize(entity),
        },
    )
