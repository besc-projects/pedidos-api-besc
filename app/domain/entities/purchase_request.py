from datetime import datetime
from typing import Optional

from app.domain.enums.purchase_request_status import PurchaseRequestStatus
from app.domain.exceptions import ValidationException


class PurchaseRequest:
    """Domain entity that owns the purchase-request business rules.

    It is framework-agnostic: it knows nothing about FastAPI, SQLAlchemy,
    HTTP or Pydantic. It only guarantees the consistency of its own state.
    """

    def __init__(
        self,
        *,
        order_id: int,
        product_id: int,
        part_number: str,
        released_quantity: float,
        requested_quantity: float,
        supplier_product_code: Optional[str] = None,
        status: Optional[PurchaseRequestStatus] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.order_id = order_id
        self.product_id = product_id
        self.part_number = part_number
        self.supplier_product_code = supplier_product_code
        self.released_quantity = released_quantity
        self.requested_quantity = requested_quantity
        self.created_at = created_at
        self.updated_at = updated_at

        self._ensure_valid_quantities()
        self.status = status if status is not None else self.resolve_status()

    def _ensure_valid_quantities(self) -> None:
        """Enforce the quantity invariants of the domain object."""
        if self.requested_quantity <= 0:
            raise ValidationException("Requested quantity must be greater than zero.")
        if self.released_quantity < 0:
            raise ValidationException("Released quantity cannot be negative.")

    def resolve_status(self) -> PurchaseRequestStatus:
        """Business rule: released >= requested -> COMPLETED, else PENDING."""
        if self.released_quantity >= self.requested_quantity:
            return PurchaseRequestStatus.COMPLETED
        return PurchaseRequestStatus.PENDING

    def needs_purchase(self) -> bool:
        """Only products with released quantity below the request need buying."""
        return self.released_quantity < self.requested_quantity

    def change_quantities(
        self,
        released_quantity: Optional[float] = None,
        requested_quantity: Optional[float] = None,
    ) -> None:
        """Update quantities and re-derive the status from the business rule."""
        if released_quantity is not None:
            self.released_quantity = released_quantity
        if requested_quantity is not None:
            self.requested_quantity = requested_quantity

        self._ensure_valid_quantities()
        self.status = self.resolve_status()
