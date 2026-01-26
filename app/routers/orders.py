from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.orders import (
    create_order,
    get_order_with_products,
    get_all_orders,
    update_order_status,
    delete_order,
)
from app.schemas.orders import (
    OrderCreate,
    OrderWithProducts,
    OrderResponse,
    OrderUpdater,
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


@router.get("/get_order/{id}", response_model=OrderWithProducts)
async def get_order(id: int, db: AsyncSession = Depends(get_db)):
    return await get_order_with_products(db, id)


@router.put("/{id}", response_model=OrderWithProducts)
async def update(id: int, data: OrderUpdater, db: AsyncSession = Depends(get_db)):
    return await update_order_status(db, id, data.status_id)


@router.delete("/{id}", response_model=dict)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    await delete_order(db, id)
    return {"detail": "Order Deleted"}
