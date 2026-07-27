from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.database import get_db
from app.domain.protocols.order_repository import OrderRepositoryProtocol
from app.infrastructure.repositories.order_repository import SqlAlchemyOrderRepository


def get_order_repository(
    db: AsyncSession = Depends(get_db),
) -> OrderRepositoryProtocol:
    return SqlAlchemyOrderRepository(db)


def get_create_order_use_case(
    repository: OrderRepositoryProtocol = Depends(get_order_repository),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(repository)


def get_get_order_with_products_use_case(
    repository: OrderRepositoryProtocol = Depends(get_order_repository),
) -> GetOrderWithProductsUseCase:
    return GetOrderWithProductsUseCase(repository)


def get_list_pending_orders_use_case(
    repository: OrderRepositoryProtocol = Depends(get_order_repository),
) -> ListPendingOrdersUseCase:
    return ListPendingOrdersUseCase(repository)


def get_list_orders_by_status_use_case(
    repository: OrderRepositoryProtocol = Depends(get_order_repository),
) -> ListOrdersByStatusUseCase:
    return ListOrdersByStatusUseCase(repository)


def get_list_orders_with_tax_reference_use_case(
    repository: OrderRepositoryProtocol = Depends(get_order_repository),
) -> ListOrdersWithTaxReferenceUseCase:
    return ListOrdersWithTaxReferenceUseCase(repository)


def get_update_order_status_use_case(
    repository: OrderRepositoryProtocol = Depends(get_order_repository),
) -> UpdateOrderStatusUseCase:
    return UpdateOrderStatusUseCase(repository)


def get_update_order_use_case(
    repository: OrderRepositoryProtocol = Depends(get_order_repository),
) -> UpdateOrderUseCase:
    return UpdateOrderUseCase(repository)


def get_delete_order_use_case(
    repository: OrderRepositoryProtocol = Depends(get_order_repository),
) -> DeleteOrderUseCase:
    return DeleteOrderUseCase(repository)
