from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class InvoiceCreate(BaseModel):
    """Payload to register an issued invoice (nota fiscal emitida)."""

    order_id: int = Field(..., alias="orderId")
    supra_id: int = Field(..., alias="supraId")
    issue_code: str = Field(..., alias="issueCode", min_length=1)
    transmission_code: Optional[str] = Field(None, alias="transmissionCode")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "orderId": 715,
                "supraId": 1403,
                "issueCode": "2032",
                "transmissionCode": None,
            }
        },
    )


class InvoiceUpdate(BaseModel):
    """Editable fields — usado na etapa 2 para gravar o código de transmissão."""

    transmission_code: Optional[str] = Field(None, alias="transmissionCode")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class InvoiceFilter(BaseModel):
    """Query filters for listing invoices."""

    order_id: Optional[int] = Field(None, alias="orderId")
    pending_transmission: Optional[bool] = Field(None, alias="pendingTransmission")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class InvoiceResponse(BaseModel):
    """API representation of an invoice."""

    id: int
    order_id: int
    supra_id: int
    issue_code: str
    transmission_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
