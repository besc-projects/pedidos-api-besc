from typing import Optional

from app.domain.entities.purchase_request import PurchaseRequest
from app.domain.enums.purchase_request_status import PurchaseRequestStatus


class FakePurchaseRequestRepository:
    """In-memory repository used to unit-test use cases without a database.

    It honors PurchaseRequestRepositoryProtocol, which is exactly why the use
    cases can depend on the abstraction and be tested in isolation.
    """

    def __init__(self, seed: Optional[list[PurchaseRequest]] = None) -> None:
        self._items: list[PurchaseRequest] = list(seed or [])
        self._next_id = 1

    async def get_by_id(
        self, purchase_request_id: int
    ) -> Optional[PurchaseRequest]:
        return next(
            (item for item in self._items if item.id == purchase_request_id), None
        )

    async def get_by_order_and_part_number(
        self, order_id: int, part_number: str
    ) -> Optional[PurchaseRequest]:
        return next(
            (
                item
                for item in self._items
                if item.order_id == order_id and item.part_number == part_number
            ),
            None,
        )

    async def list_by_order(
        self, order_id: int, status: Optional[PurchaseRequestStatus] = None
    ) -> list[PurchaseRequest]:
        return [
            item
            for item in self._items
            if item.order_id == order_id
            and (status is None or item.status == status)
        ]

    async def create(self, purchase_request: PurchaseRequest) -> PurchaseRequest:
        purchase_request.id = self._next_id
        self._next_id += 1
        self._items.append(purchase_request)
        return purchase_request

    async def update(self, purchase_request: PurchaseRequest) -> PurchaseRequest:
        return purchase_request
