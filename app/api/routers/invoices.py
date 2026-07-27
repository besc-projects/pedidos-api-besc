from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.dependencies.invoices import (
    get_create_invoice_use_case,
    get_list_invoices_use_case,
    get_update_invoice_use_case,
)
from app.application.use_cases.invoices.create_invoice import CreateInvoiceUseCase
from app.application.use_cases.invoices.list_invoices import ListInvoicesUseCase
from app.application.use_cases.invoices.update_invoice import UpdateInvoiceUseCase
from app.schemas.invoices import (
    InvoiceCreate,
    InvoiceFilter,
    InvoiceResponse,
    InvoiceUpdate,
)

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


def _serialize(entity) -> dict:
    return jsonable_encoder(
        InvoiceResponse.model_validate(entity, from_attributes=True)
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Register an issued invoice",
    description=(
        "Registers the nota fiscal issued for an order (stage 1). "
        "Rejects a duplicate for the same order."
    ),
    responses={
        201: {"description": "Invoice created successfully."},
        400: {"description": "Invalid data."},
        409: {"description": "An invoice already exists for this order."},
    },
)
async def create_invoice(
    data: InvoiceCreate,
    use_case: CreateInvoiceUseCase = Depends(get_create_invoice_use_case),
) -> JSONResponse:
    entity = await use_case.execute(data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Invoice created successfully.",
            "invoice": _serialize(entity),
        },
    )


@router.get(
    "/",
    summary="List invoices",
    description=(
        "Lists invoices, optionally filtered by order or by pending "
        "transmission (transmission_code still empty)."
    ),
    responses={200: {"description": "Invoices retrieved successfully."}},
)
async def list_invoices(
    order_id: int | None = Query(None, alias="orderId"),
    pending_transmission: bool | None = Query(None, alias="pendingTransmission"),
    use_case: ListInvoicesUseCase = Depends(get_list_invoices_use_case),
) -> JSONResponse:
    filters = InvoiceFilter(order_id=order_id, pending_transmission=pending_transmission)
    entities = await use_case.execute(filters)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Invoices retrieved successfully.",
            "total": len(entities),
            "invoices": [_serialize(entity) for entity in entities],
        },
    )


@router.put(
    "/{invoice_id}",
    summary="Update an invoice",
    description="Grava o transmission_code na etapa 2 (transmissão da NF-e).",
    responses={
        200: {"description": "Invoice updated successfully."},
        400: {"description": "No fields to update."},
        404: {"description": "Invoice not found."},
    },
)
async def update_invoice(
    invoice_id: int,
    data: InvoiceUpdate,
    use_case: UpdateInvoiceUseCase = Depends(get_update_invoice_use_case),
) -> JSONResponse:
    entity = await use_case.execute(invoice_id, data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Invoice updated successfully.",
            "invoice": _serialize(entity),
        },
    )
