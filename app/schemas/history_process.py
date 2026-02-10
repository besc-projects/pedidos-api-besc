from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime


class HistoryProcessBase(BaseModel):
    orders: str = Field(..., max_length=64, description="Número do pedido")
    step: str = Field(..., max_length=20, description="Etapa do processo")
    id_situation: int = Field(
        ..., gt=0, description="ID da situação (deve ser maior que 0)"
    )

    @field_validator("id_situation")
    @classmethod
    def validate_id_situation(cls, v):
        if v <= 0:
            raise ValueError("id_situation deve ser maior que 0")
        return v


class HistoryProcessCreate(HistoryProcessBase):
    pass


class HistoryProcessResponse(HistoryProcessBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoryProcessListResponse(BaseModel):
    total: int
    items: list[HistoryProcessResponse]
