from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FiscalNotificationCreate(BaseModel):
    """Payload to register that a product's missing-fiscal-registration
    warning has been sent."""

    part_number: str = Field(..., alias="partNumber", min_length=1)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={"example": {"partNumber": "EF04862"}},
    )


class FiscalNotificationResponse(BaseModel):
    """API representation of a single fiscal notification record."""

    id: int
    part_number: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
