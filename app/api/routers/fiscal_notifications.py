from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.dependencies.fiscal_notifications import (
    get_create_fiscal_notification_use_case,
    get_get_fiscal_notification_use_case,
)
from app.application.use_cases.fiscal_notifications.create_fiscal_notification import (
    CreateFiscalNotificationUseCase,
)
from app.application.use_cases.fiscal_notifications.get_fiscal_notification import (
    GetFiscalNotificationUseCase,
)
from app.schemas.fiscal_notifications import (
    FiscalNotificationCreate,
    FiscalNotificationResponse,
)

router = APIRouter(prefix="/api/fiscal-notifications")


def _serialize(entity) -> dict:
    return jsonable_encoder(
        FiscalNotificationResponse.model_validate(entity, from_attributes=True)
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Register that a product's missing-fiscal-registration warning was sent",
    description=(
        "Marks a product as already notified for missing fiscal registration "
        "(dbo.sgr_cadastro_produto_fiscal in SUPRA). Idempotent: calling it again "
        "for the same part number returns the existing record instead of erroring."
    ),
    responses={201: {"description": "Fiscal notification registered successfully."}},
)
async def create_fiscal_notification(
    data: FiscalNotificationCreate,
    use_case: CreateFiscalNotificationUseCase = Depends(
        get_create_fiscal_notification_use_case
    ),
) -> JSONResponse:
    entity = await use_case.execute(data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Fiscal notification registered successfully.",
            "fiscal_notification": _serialize(entity),
        },
    )


@router.get(
    "/{part_number}",
    summary="Check whether a product was already notified for missing fiscal registration",
    responses={
        200: {"description": "Fiscal notification found."},
        404: {"description": "Fiscal notification not found."},
    },
)
async def get_fiscal_notification(
    part_number: str,
    use_case: GetFiscalNotificationUseCase = Depends(get_get_fiscal_notification_use_case),
) -> JSONResponse:
    entity = await use_case.execute(part_number)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Fiscal notification found.",
            "fiscal_notification": _serialize(entity),
        },
    )
