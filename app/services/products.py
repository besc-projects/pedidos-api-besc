from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException
from app.models.orders import Order as OrderModel
from app.models.products import Product as ProductModel
from app.models.taxs import Tax as TaxRecordModel
from app.schemas.products import (
    ProductCreate,
    ProductResponse,
    ProductStockStatusUpdate,
)


# 🟢 Create product
async def create_product(
    db: AsyncSession, product_in: ProductCreate
) -> ProductResponse:
    # Validate order
    result = await db.execute(
        select(OrderModel).where(OrderModel.vale_order_id == product_in.order_id)
    )
    order = result.scalars().first()
    if not order:
        raise HTTPException(404, "Order not found")

    # Validate tax record (if provided)
    if product_in.tax_id:
        result = await db.execute(
            select(TaxRecordModel).where(TaxRecordModel.id == product_in.tax_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(400, "Invalid tax record ID — record not found.")

    # Create product
    db_product = ProductModel(**product_in.model_dump())
    db_product.order_id = order.id
    db.add(db_product)

    try:
        await db.commit()
        await db.refresh(db_product)
    except Exception as e:
        await db.rollback()
        raise HTTPException(400, "Error while saving product.")

    return ProductResponse.model_validate(db_product, from_attributes=True)


# 🔵 Get product by ID
async def get_product(db: AsyncSession, item_id: int) -> ProductResponse:
    result = await db.execute(select(ProductModel).filter(ProductModel.id == item_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")
    return ProductResponse.model_validate(product)


# 🟣 Get products by order
async def get_products_by_order(db: AsyncSession, order_id: int):
    result = await db.execute(
        select(ProductModel).filter(ProductModel.order_id == order_id)
    )
    return [ProductResponse.model_validate(p) for p in result.scalars().all()]


# 🟠 Update product
async def update_product(
    db: AsyncSession, item_id: int, product_in: ProductStockStatusUpdate
) -> ProductResponse:
    # Check if product exists
    result = await db.execute(select(ProductModel).filter(ProductModel.id == item_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == item_id)
        .values(stock_status_id=product_in.stock_status_id)
    )
    await db.commit()
    return await get_product(db, item_id)


# 🔴 Delete product
async def delete_product(db: AsyncSession, item_id: int):
    result = await db.execute(select(ProductModel).filter(ProductModel.id == item_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")

    await db.execute(delete(ProductModel).where(ProductModel.id == item_id))
    await db.commit()
