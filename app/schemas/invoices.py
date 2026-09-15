from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class InvoiceCreate(BaseModel):
    """Payload to register an issued invoice (nota fiscal emitida)."""

    order_id: int = Field(..., alias="orderId")
    id_emissao: int = Field(..., alias="idEmissao")
    data: datetime = Field(..., alias="data")
    id_transmissao: Optional[int] = Field(None, alias="idTransmissao")
    nfe: Optional[str] = Field(None, alias="nfe")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "orderId": 715,
                "idEmissao": 2032,
                "data": "2026-09-14T16:41:00Z",
                "idTransmissao": None,
                "nfe": None,
            }
        },
    )


class InvoiceUpdate(BaseModel):
    """Editable fields — usado na etapa 2 para gravar transmissão/NF-e."""

    id_transmissao: Optional[int] = Field(None, alias="idTransmissao")
    nfe: Optional[str] = Field(None, alias="nfe")

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
    id_emissao: int
    data: datetime
    id_transmissao: Optional[int] = None
    nfe: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
