from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FiscalNotificationCreate(BaseModel):
    """Payload to register that a product's missing-fiscal-registration
    warning has been sent."""

    part_number: str = Field(..., alias="partNumber", min_length=1)
    # Pedido que disparou o aviso — só contexto/auditoria, não entra no dedup
    # (que continua por part_number). Opcional: quem chamar sem saber o
    # pedido (ou não tiver um) ainda consegue marcar a notificação.
    vale_order_id: Optional[int] = Field(None, alias="valeOrderId")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={"example": {"partNumber": "EF04862", "valeOrderId": 4513535908}},
    )


class FiscalNotificationResponse(BaseModel):
    """API representation of a single fiscal notification record."""

    id: int
    part_number: str
    vale_order_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
