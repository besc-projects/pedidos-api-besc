from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SeverityEnum(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"


class HistoryProcessBase(BaseModel):
    order_id: int = Field(..., gt=0, description="ID do pedido")
    step: str = Field(..., max_length=80, description="Etapa do processo")
    description: str = Field(..., description="Descrição detalhada do evento")
    severity: SeverityEnum = Field(
        default=SeverityEnum.info, description="Severidade do evento"
    )
    created_by: Optional[str] = Field(
        None, max_length=120, description="Email/login/nome do robot que criou o evento"
    )
    occurred_at: Optional[datetime] = Field(None, description="Quando o evento ocorreu")


class HistoryProcessCreate(HistoryProcessBase):
    pass


class HistoryProcessResponse(HistoryProcessBase):
    id: int
    created_at: datetime
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoryProcessListResponse(BaseModel):
    total: int
    items: list[HistoryProcessResponse]
