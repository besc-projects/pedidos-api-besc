from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.orders import (
    create_order,
    get_order_with_products,
    get_all_orders,
    get_orders_by_status,
    get_orders_with_tax_reference_by_status,
    update_order_status,
    update_order,
    delete_order,
)
from app.schemas.orders import (
    OrderCreate,
    OrderWithProducts,
    OrderResponse,
    OrderUpdater,
    OrderStatusFilter,
    OrderUpdate,
)

router = APIRouter(prefix="/api/orders")


@router.post("/", response_model=OrderResponse)
async def create(pedido: OrderCreate, db: AsyncSession = Depends(get_db)):
    return await create_order(db, pedido)


@router.get("/pending", response_model=list[OrderWithProducts])
async def get_all(
    db: AsyncSession = Depends(get_db), skip: int = Query(0), limit: int = Query(100)
):
    return await get_all_orders(db, skip, limit)


@router.get("/status")
async def get_all_by_status(
    process_id: int = Query(...),
    status_code: int = Query(...),
    skip: int = Query(0),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db),
):
    return await get_orders_by_status(
        db=db,
        process_id=process_id,
        status_code=status_code,
        skip=skip,
        limit=limit,
    )


@router.get("/status/tax-reference")
async def get_orders_with_tax_reference(
    process_id: int = Query(...),
    status_code: int = Query(...),
    vale_order_id: int | None = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db),
):
    return await get_orders_with_tax_reference_by_status(
        db=db,
        process_id=process_id,
        status_code=status_code,
        vale_order_id=vale_order_id,
        skip=skip,
        limit=limit,
    )


@router.get("/get_order/{id}", response_model=OrderWithProducts)
async def get_order(id: int, db: AsyncSession = Depends(get_db)):
    return await get_order_with_products(db, id)


@router.put("/status/{id}", response_model=OrderWithProducts)
async def update_status(
    id: int, data: OrderUpdater, db: AsyncSession = Depends(get_db)
):
    """Update the process and status code of an order."""
    return await update_order_status(db, id, data.process_id, data.status_code)


@router.patch("/{id}", response_model=OrderWithProducts)
async def update(id: int, data: OrderUpdate, db: AsyncSession = Depends(get_db)):
    """Update any fields of an order. Only provided fields will be updated."""
    return await update_order(db, id, data)


@router.delete("/{id}", response_model=dict)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    await delete_order(db, id)
    return {"detail": "Order Deleted"}
