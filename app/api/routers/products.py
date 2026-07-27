from typing import List

from fastapi import APIRouter, Depends, status

from app.api.dependencies.products import (
    get_create_product_use_case,
    get_get_product_use_case,
    get_list_products_by_order_use_case,
    get_update_product_use_case,
)
from app.application.use_cases.products.use_cases import (
    CreateProductUseCase,
    GetProductUseCase,
    ListProductsByOrderUseCase,
    UpdateProductUseCase,
)
from app.schemas.products import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("/{id}", response_model=ProductResponse, summary="Get a product by id")
async def get_product_by_id(
    id: int,
    use_case: GetProductUseCase = Depends(get_get_product_use_case),
) -> ProductResponse:
    return await use_case.execute(id)


@router.get(
    "/order/{order_id}",
    response_model=List[ProductResponse],
    summary="List products of an order",
)
async def get_products_for_order(
    order_id: int,
    use_case: ListProductsByOrderUseCase = Depends(
        get_list_products_by_order_use_case
    ),
) -> List[ProductResponse]:
    return await use_case.execute(order_id)


@router.post(
    "/bulk/order/{order_id}",
    response_model=List[ProductResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple products for an order",
)
async def create_products_bulk(
    order_id: int,
    products: List[ProductCreate],
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),
) -> List[ProductResponse]:
    created = []
    for product in products:
        product.order_id = order_id
        created.append(await use_case.execute(product))
    return created


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update a product by id",
)
async def update_product_by_id(
    product_id: int,
    product_in: ProductUpdate,
    use_case: UpdateProductUseCase = Depends(get_update_product_use_case),
) -> ProductResponse:
    return await use_case.execute(product_id, product_in)
