from app.domain.entities.purchase_request import PurchaseRequest
from app.domain.protocols.purchase_request_repository import (
    PurchaseRequestRepositoryProtocol,
)
from app.schemas.purchase_requests import PurchaseRequestFilter


class ListPurchaseRequestsUseCase:
    """List the purchase requests of an order, optionally filtered by status."""

    def __init__(self, repository: PurchaseRequestRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, filters: PurchaseRequestFilter) -> list[PurchaseRequest]:
        if filters.order_id is None:
            return await self._repository.list_all(filters.status)
        return await self._repository.list_by_order(filters.order_id, filters.status)
