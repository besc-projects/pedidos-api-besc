from app.domain.entities.purchase_request import PurchaseRequest
from app.domain.exceptions import BusinessException, ConflictException
from app.domain.protocols.purchase_request_repository import (
    PurchaseRequestRepositoryProtocol,
)
from app.schemas.purchase_requests import PurchaseRequestCreate


class CreatePurchaseRequestUseCase:
    """Register a product whose released quantity is below the requested one."""

    def __init__(self, repository: PurchaseRequestRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: PurchaseRequestCreate) -> PurchaseRequest:
        purchase_request = PurchaseRequest(
            order_id=data.order_id,
            product_id=data.product_id,
            part_number=data.part_number,
            supplier_product_code=data.supplier_product_code,
            released_quantity=data.released_quantity,
            requested_quantity=data.requested_quantity,
        )

        if not purchase_request.needs_purchase():
            raise BusinessException(
                "Released quantity already meets the request; no purchase needed."
            )

        already_exists = await self._repository.get_by_order_and_part_number(
            purchase_request.order_id, purchase_request.part_number
        )
        if already_exists is not None:
            raise ConflictException(
                "A purchase request already exists for this order and part number."
            )

        return await self._repository.create(purchase_request)
