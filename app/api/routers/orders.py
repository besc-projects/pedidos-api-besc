from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.dependencies.orders import (
    get_create_order_use_case,
    get_delete_order_use_case,
    get_get_order_with_products_use_case,
    get_list_orders_by_status_use_case,
    get_list_orders_with_tax_reference_use_case,
    get_list_pending_orders_use_case,
    get_update_order_status_use_case,
    get_update_order_use_case,
)
from app.application.use_cases.orders.use_cases import (
    CreateOrderUseCase,
    DeleteOrderUseCase,
    GetOrderWithProductsUseCase,
    ListOrdersByStatusUseCase,
    ListOrdersWithTaxReferenceUseCase,
    ListPendingOrdersUseCase,
    UpdateOrderStatusUseCase,
    UpdateOrderUseCase,
)
from app.domain.entities.order import Order
from app.domain.entities.product import Product
from app.schemas.orders import (
    OrderCreate,
    OrderResponse,
    OrderUpdate,
    OrderUpdater,
)

router = APIRouter(prefix="/api/orders", tags=["Orders"])


def _serialize_order(order: Order, products: list[Product]) -> dict:
    data = OrderResponse.model_validate(order, from_attributes=True).model_dump()
    data["products"] = [
        product.__dict__.copy() for product in products
    ]
    return jsonable_encoder(data)


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create an order")
async def create(
    order: OrderCreate,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
) -> JSONResponse:
    created = await use_case.execute(order)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Order created successfully!",
            "order": jsonable_encoder(
                OrderResponse.model_validate(created, from_attributes=True)
            ),
        },
    )


@router.get("/pending", summary="List pending orders")
async def get_all(
    skip: int = Query(0),
    limit: int = Query(100),
    use_case: ListPendingOrdersUseCase = Depends(get_list_pending_orders_use_case),
) -> JSONResponse:
    orders = await use_case.execute(skip, limit)
    payload = [_serialize_order(order, products) for order, products in orders]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Orders retrieved successfully!",
            "total": len(payload),
            "orders": payload,
        },
    )


@router.get("/status", summary="List orders by process and status")
async def get_all_by_status(
    process_id: int = Query(...),
    status_code: int = Query(...),
    skip: int = Query(0),
    limit: int = Query(100),
    use_case: ListOrdersByStatusUseCase = Depends(get_list_orders_by_status_use_case),
) -> JSONResponse:
    orders = await use_case.execute(process_id, status_code, skip, limit)
    payload = [_serialize_order(order, products) for order, products in orders]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Orders retrieved successfully!",
            "process_id": process_id,
            "status_code": status_code,
            "total": len(payload),
            "orders": payload,
        },
    )


@router.get("/status/tax-reference", summary="List orders with tax references")
async def get_orders_with_tax_reference(
    vale_order_id: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    use_case: ListOrdersWithTaxReferenceUseCase = Depends(
        get_list_orders_with_tax_reference_use_case
    ),
) -> JSONResponse:
    orders = await use_case.execute(vale_order_id, skip, limit)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            {
                "message": "Orders retrieved successfully!",
                "total": len(orders),
                "orders": orders,
            }
        ),
    )


@router.get("/get_order/{id}", summary="Get an order with its products")
async def get_order(
    id: int,
    use_case: GetOrderWithProductsUseCase = Depends(
        get_get_order_with_products_use_case
    ),
) -> JSONResponse:
    order, products = await use_case.execute(id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Order found!", "order": _serialize_order(order, products)},
    )


@router.put("/status/{id}", summary="Update the process and status of an order")
async def update_status(
    id: int,
    data: OrderUpdater,
    use_case: UpdateOrderStatusUseCase = Depends(get_update_order_status_use_case),
) -> JSONResponse:
    order = await use_case.execute(id, data.process_id, data.status_code)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Status updated!",
            "order": jsonable_encoder(
                OrderResponse.model_validate(order, from_attributes=True)
            ),
        },
    )


@router.patch("/{id}", summary="Update an order")
async def update(
    id: int,
    data: OrderUpdate,
    use_case: UpdateOrderUseCase = Depends(get_update_order_use_case),
) -> JSONResponse:
    updated_fields, order = await use_case.execute(id, data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Order updated successfully!",
            "updated_fields": updated_fields,
            "order": jsonable_encoder(
                OrderResponse.model_validate(order, from_attributes=True)
            ),
        },
    )


@router.delete("/{id}", summary="Delete an order")
async def delete(
    id: int,
    use_case: DeleteOrderUseCase = Depends(get_delete_order_use_case),
) -> dict:
    await use_case.execute(id)
    return {"detail": "Order Deleted"}
