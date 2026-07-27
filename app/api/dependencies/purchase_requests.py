from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.purchase_requests.create_purchase_request import (
    CreatePurchaseRequestUseCase,
)
from app.application.use_cases.purchase_requests.list_purchase_requests import (
    ListPurchaseRequestsUseCase,
)
from app.application.use_cases.purchase_requests.update_purchase_request import (
    UpdatePurchaseRequestUseCase,
)
from app.database import get_db
from app.domain.protocols.purchase_request_repository import (
    PurchaseRequestRepositoryProtocol,
)
from app.infrastructure.repositories.purchase_request_repository import (
    SqlAlchemyPurchaseRequestRepository,
)


def get_purchase_request_repository(
    db: AsyncSession = Depends(get_db),
) -> PurchaseRequestRepositoryProtocol:
    """Provide the concrete repository behind its protocol."""
    return SqlAlchemyPurchaseRequestRepository(db)


def get_create_purchase_request_use_case(
    repository: PurchaseRequestRepositoryProtocol = Depends(
        get_purchase_request_repository
    ),
) -> CreatePurchaseRequestUseCase:
    return CreatePurchaseRequestUseCase(repository)


def get_update_purchase_request_use_case(
    repository: PurchaseRequestRepositoryProtocol = Depends(
        get_purchase_request_repository
    ),
) -> UpdatePurchaseRequestUseCase:
    return UpdatePurchaseRequestUseCase(repository)


def get_list_purchase_requests_use_case(
    repository: PurchaseRequestRepositoryProtocol = Depends(
        get_purchase_request_repository
    ),
) -> ListPurchaseRequestsUseCase:
    return ListPurchaseRequestsUseCase(repository)
