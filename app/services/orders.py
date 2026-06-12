from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orders import Order as OrderModel
from app.models.proposals import Proposal as ProposalModel
from app.models.products import Product as ProductModel
from app.models.tax_reference import TaxReferenceProductSupra as TaxReferenceModel
from app.schemas.orders import OrderCreate, OrderWithProducts, OrderUpdate
from sqlalchemy.orm import selectinload


def _order_response_schema(order: OrderModel, products=None):
    order_data = order.__dict__.copy()
    if order_data.get("process_id") is None:
        order_data["process_id"] = 0
    if order_data.get("status_code") is None:
        order_data["status_code"] = 0
    if products is not None:
        order_data["products"] = products
    return OrderWithProducts.model_validate(order_data, from_attributes=True).model_dump()


async def create_order(db: AsyncSession, data: OrderCreate) -> JSONResponse:
    try:

        # 🟢 Create main order
        order = OrderModel(**data.model_dump(exclude={"products"}))
        order.process_id = 1  # Default process for new orders
        order.status_code = 0  # Default status for new orders
        db.add(order)
        await db.commit()
        await db.refresh(order)

        # ✅ Serialize safely
        order_data = jsonable_encoder(order)
        return JSONResponse(
            status_code=201,
            content={
                "message": "Order created successfully!",
                "order": order_data,
            },
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal error while creating order",
                "error": str(e),
            },
        )


# 🔵 Get order with products
async def get_order_with_products(db: AsyncSession, order_number: int):
    result = await db.execute(
        select(OrderModel).where(OrderModel.vale_order_id == order_number)
    )
    order = result.scalars().first()

    if not order:
        return JSONResponse(status_code=404, content={"message": "Order not found"})

    # Get linked products
    result_prod = await db.execute(
        select(ProductModel).where(ProductModel.order_id == order.id)
    )
    products = result_prod.scalars().all()

    # Build response schema
    order_schema = _order_response_schema(order, products)
    order_data = jsonable_encoder(order_schema)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Order found!",
            "order": order_data,
        },
    )


async def update_order_status(
    db: AsyncSession, vale_order_id: int, process_id: int, status_code: int
):
    result = await db.execute(
        select(OrderModel).where(OrderModel.vale_order_id == vale_order_id)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(404, "Order not found")

    order.process_id = process_id
    order.status_code = status_code
    await db.commit()
    await db.refresh(order)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Status updated!",
            "order": jsonable_encoder(order),
        },
    )


async def update_order(db: AsyncSession, vale_order_id: int, data: OrderUpdate):
    """Updates an order with only the fields provided in the request."""
    try:
        result = await db.execute(
            select(OrderModel).where(OrderModel.vale_order_id == vale_order_id)
        )
        order = result.scalars().first()

        if not order:
            return JSONResponse(status_code=404, content={"message": "Order not found"})

        # Get only the fields that were actually provided (not None)
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return JSONResponse(
                status_code=400, content={"message": "No fields to update"}
            )

        # Update only the provided fields
        for field, value in update_data.items():
            if hasattr(order, field):
                setattr(order, field, value)

        await db.commit()
        await db.refresh(order)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Order updated successfully!",
                "updated_fields": list(update_data.keys()),
                "order": jsonable_encoder(order),
            },
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal error while updating order",
                "error": str(e),
            },
        )


# 🔴 Delete order
async def delete_order(db: AsyncSession, order_id: int):
    try:
        result = await db.execute(select(OrderModel).where(OrderModel.id == order_id))
        order = result.scalars().first()

        if not order:
            return JSONResponse(status_code=404, content={"message": "Order not found"})

        # Delete linked products first (FK)
        await db.execute(delete(ProductModel).where(ProductModel.order_id == order_id))
        await db.commit()

        # Delete the order itself
        await db.delete(order)
        await db.commit()

        return JSONResponse(
            status_code=200, content={"message": "Order deleted successfully!"}
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={"message": "Internal error while deleting order", "error": str(e)},
        )


# 🔵 Get single order
async def get_order(db: AsyncSession, order_id: int):
    result = await db.execute(
        select(OrderModel).where(OrderModel.vale_order_id == order_id)
    )
    order = result.scalars().first()

    if not order:
        return JSONResponse(status_code=404, content={"message": "Order not found"})

    # Fetch linked products
    result_products = await db.execute(
        select(ProductModel).where(ProductModel.order_id == order.id)
    )
    products = result_products.scalars().all()

    return JSONResponse(
        status_code=200,
        content={
            "message": "Order found!",
            "order": _order_response_schema(order, products),
        },
    )


async def get_all_orders(db: AsyncSession, skip: int = 0, limit: int = 10):
    PROCESS_ID_ORDERS = 1
    STATUS_CODE_PENDING = 0
    result = await db.execute(
        select(OrderModel)
        .options(selectinload(OrderModel.products))
        .options(
            selectinload(OrderModel.proposals).selectinload(
                ProposalModel.proposals_status
            )
        )
        .offset(skip)
        .limit(limit)
        .filter(OrderModel.process_id == PROCESS_ID_ORDERS, OrderModel.status_code == STATUS_CODE_PENDING)
    )

    # Get unique order
    orders = result.scalars().unique().all()

    if not orders:
        return JSONResponse(status_code=404, content={"message": "No orders found"})

    orders_schema = []
    for order in orders:
        order_data = _order_response_schema(order)

        proposal_status = None
        if order.proposals and order.proposals.proposals_status:
            proposal_status = {
                "id": order.proposals.proposals_status.id,
                "description": order.proposals.proposals_status.description,
            }

        order_data["proposal_status"] = proposal_status
        orders_schema.append(order_data)

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {
                "message": "Orders retrieved successfully!",
                "total": len(orders_schema),
                "orders": orders_schema,
            }
        ),
    )


async def get_orders_by_status(
    db: AsyncSession, process_id: int, status_code: int, skip: int = 0, limit: int = 10
):
    result = await db.execute(
        select(OrderModel)
        .options(selectinload(OrderModel.products))
        .options(
            selectinload(OrderModel.proposals)
            .selectinload(
                ProposalModel.proposals_status
            )
        )
        .offset(skip)
        .limit(limit)
        .filter(
            OrderModel.process_id == process_id,
            OrderModel.status_code == status_code,
        )
    )

    orders = result.scalars().unique().all()

    if not orders:
        return JSONResponse(
            status_code=404,
            content={
                "message": f"No orders found for process_id={process_id} and status_code={status_code}"
            },
        )

    orders_schema = []
    for order in orders:
        order_data = _order_response_schema(order)

        proposal_status = None
        if order.proposals and order.proposals.proposals_status:
            proposal_status = {
                "id": order.proposals.proposals_status.id,
                "description": order.proposals.proposals_status.description,
            }

        order_data["proposal_status"] = proposal_status
        orders_schema.append(order_data)

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {
                "message": "Orders retrieved successfully!",
                "process_id": process_id,
                "status_code": status_code,
                "total": len(orders_schema),
                "orders": orders_schema,
            }
        ),
    )


async def get_orders_with_tax_reference_by_status(
    db: AsyncSession,
    vale_order_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = (
        select(OrderModel, ProductModel, TaxReferenceModel)
        .join(ProductModel, ProductModel.order_id == OrderModel.id)
        .join(TaxReferenceModel, TaxReferenceModel.id_product == ProductModel.id)
        .filter(
            OrderModel.process_id == 2,
            OrderModel.status_code == 1,
        )
        .offset(skip)
        .limit(limit)
    )

    if vale_order_id is not None:
        query = query.filter(OrderModel.vale_order_id == vale_order_id)

    result = await db.execute(query)
    rows = result.all()

    if not rows:
        return JSONResponse(
            status_code=404,
            content={
                "message": (
                    f"No orders found for process_id=2, "
                    f"status_code=1"
                    + (
                        f", vale_order_id={vale_order_id}"
                        if vale_order_id is not None
                        else ""
                    )
                )
            },
        )

    orders_map = {}
    order_seen_products = {}
    for order, product, tax_ref in rows:
        if order.id not in orders_map:
            orders_map[order.id] = {
                "vale_order_id": int(order.vale_order_id),
                "state": str(order.state or "").strip().upper(),
                "proposal_id": order.proposal_id,
                "products": [],
                "besc_order_id": order.besc_order_id,
                "invoice_number": order.invoice_number,
                "center": order.center,
            }
            order_seen_products[order.id] = set()

        if tax_ref.id_product in order_seen_products[order.id]:
            continue

        order_seen_products[order.id].add(tax_ref.id_product)
        orders_map[order.id]["products"].append(
            {
                "product_id": product.id,
                "item": product.item,
                "part_number": product.part_number,
                "description": product.description,
                "ncm_code": tax_ref.ncm_code,
                "ipi": float(tax_ref.ipi) if tax_ref.ipi is not None else None,
                "icms": float(tax_ref.icms) if tax_ref.icms is not None else None,
                "icms_st": float(tax_ref.icms_st) if tax_ref.icms_st is not None else None,
                "origin": tax_ref.origin,
                "id_product": tax_ref.id_product,
                "tax_reference_id": tax_ref.id,
                "created_at": tax_ref.created_at,
                "updated_at": tax_ref.updated_at,
            }
        )

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {
                "message": "Orders retrieved successfully!",
                "total": len(orders_map),
                "orders": list(orders_map.values()),
            }
        ),
    )
