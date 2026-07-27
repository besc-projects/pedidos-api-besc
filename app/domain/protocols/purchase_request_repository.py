from typing import Optional, Protocol

from app.domain.entities.purchase_request import PurchaseRequest
from app.domain.enums.purchase_request_status import PurchaseRequestStatus


class PurchaseRequestRepositoryProtocol(Protocol):
    """Persistence contract for purchase requests.

    Use cases depend on this abstraction, never on a concrete implementation,
    which keeps the application layer decoupled and easy to test.
    """

    async def get_by_id(self, purchase_request_id: int) -> Optional[PurchaseRequest]:
        ...

    async def get_by_order_and_part_number(
        self, order_id: int, part_number: str
    ) -> Optional[PurchaseRequest]:
        ...

    async def list_by_order(
        self, order_id: int, status: Optional[PurchaseRequestStatus] = None
    ) -> list[PurchaseRequest]:
        ...

    async def list_all(
        self, status: Optional[PurchaseRequestStatus] = None
    ) -> list[PurchaseRequest]:
        ...

    async def create(self, purchase_request: PurchaseRequest) -> PurchaseRequest:
        ...

    async def update(self, purchase_request: PurchaseRequest) -> PurchaseRequest:
        ...
