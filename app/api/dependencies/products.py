from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.products.use_cases import (
    CreateProductUseCase,
    GetProductUseCase,
    ListProductsByOrderUseCase,
    UpdateProductUseCase,
)
from app.database import get_db
from app.domain.protocols.product_repository import ProductRepositoryProtocol
from app.infrastructure.repositories.product_repository import (
    SqlAlchemyProductRepository,
)


def get_product_repository(
    db: AsyncSession = Depends(get_db),
) -> ProductRepositoryProtocol:
    return SqlAlchemyProductRepository(db)


def get_get_product_use_case(
    repository: ProductRepositoryProtocol = Depends(get_product_repository),
) -> GetProductUseCase:
    return GetProductUseCase(repository)


def get_list_products_by_order_use_case(
    repository: ProductRepositoryProtocol = Depends(get_product_repository),
) -> ListProductsByOrderUseCase:
    return ListProductsByOrderUseCase(repository)


def get_create_product_use_case(
    repository: ProductRepositoryProtocol = Depends(get_product_repository),
) -> CreateProductUseCase:
    return CreateProductUseCase(repository)


def get_update_product_use_case(
    repository: ProductRepositoryProtocol = Depends(get_product_repository),
) -> UpdateProductUseCase:
    return UpdateProductUseCase(repository)
