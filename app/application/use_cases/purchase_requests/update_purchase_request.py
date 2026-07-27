from app.domain.entities.purchase_request import PurchaseRequest
from app.domain.exceptions import NotFoundException, ValidationException
from app.domain.protocols.purchase_request_repository import (
    PurchaseRequestRepositoryProtocol,
)
from app.schemas.purchase_requests import PurchaseRequestUpdate


class UpdatePurchaseRequestUseCase:
    """Update quantities of a purchase request; status follows the business rule."""

    def __init__(self, repository: PurchaseRequestRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, purchase_request_id: int, data: PurchaseRequestUpdate
    ) -> PurchaseRequest:
        purchase_request = await self._repository.get_by_id(purchase_request_id)
        if purchase_request is None:
            raise NotFoundException("Purchase request not found.")

        changes = data.model_dump(exclude_unset=True)
        if not changes:
            raise ValidationException("No fields to update.")

        # The client-sent status is intentionally ignored: the entity always
        # recomputes it from the quantities, so the business rule prevails.
        purchase_request.change_quantities(
            released_quantity=changes.get("released_quantity"),
            requested_quantity=changes.get("requested_quantity"),
        )

        return await self._repository.update(purchase_request)
