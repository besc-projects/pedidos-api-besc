from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.purchase_request_status import PurchaseRequestStatus


class PurchaseRequestCreate(BaseModel):
    """Payload to register a product that needs to be purchased."""

    order_id: int = Field(..., alias="orderId")
    product_id: int = Field(..., alias="productId")
    supplier_product_code: Optional[str] = Field(None, alias="supplierProductCode")
    part_number: str = Field(..., alias="partNumber", min_length=1)
    released_quantity: float = Field(..., alias="releasedQuantity")
    requested_quantity: float = Field(..., alias="requestedQuantity")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "orderId": 1001,
                "productId": 20,
                "supplierProductCode": "00038",
                "partNumber": "PMN1SX",
                "releasedQuantity": 5,
                "requestedQuantity": 12,
            }
        },
    )


class PurchaseRequestUpdate(BaseModel):
    """Editable fields of a purchase request. Status is recomputed by the rule."""

    released_quantity: Optional[float] = Field(None, alias="releasedQuantity")
    requested_quantity: Optional[float] = Field(None, alias="requestedQuantity")
    status: Optional[PurchaseRequestStatus] = Field(None, alias="status")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class PurchaseRequestFilter(BaseModel):
    """Query filters for listing purchase requests.

    order_id is optional: when omitted, lists across all orders (optionally by status).
    """

    order_id: Optional[int] = Field(None, alias="orderId")
    status: Optional[PurchaseRequestStatus] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class PurchaseRequestResponse(BaseModel):
    """API representation of a single purchase request."""

    id: int
    order_id: int
    product_id: int
    supplier_product_code: Optional[str] = None
    part_number: str
    released_quantity: float
    requested_quantity: float
    status: PurchaseRequestStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
