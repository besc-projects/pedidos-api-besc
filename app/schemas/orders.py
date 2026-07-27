from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.products import ProductBase


class OrderBase(BaseModel):
    vale_order_id: int
    ticket_id: Optional[int] = None
    process_id: int = 0
    status_code: int = 0
    total_value: float
    portal: str
    center: str
    state: str
    cnpj: str
    date: datetime
    days_to_delivery: Optional[str] = None
    besc_order_id: Optional[int] = None
    contract_number: Optional[str] = None
    invoice_number: Optional[str] = None
    version: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class OrderUpdater(BaseModel):
    process_id: int = Field(..., description="ID do processo do pedido")
    status_code: int = Field(..., description="Código do status do pedido")


class OrderUpdate(BaseModel):
    """Schema for partial order updates - all fields optional."""

    process_id: Optional[int] = None
    status_code: Optional[int] = None
    ticket_id: Optional[int] = None
    total_value: Optional[float] = None
    portal: Optional[str] = None
    center: Optional[str] = None
    state: Optional[str] = None
    cnpj: Optional[str] = None
    date: Optional[datetime] = None
    days_to_delivery: Optional[str] = None
    besc_order_id: Optional[int] = None
    contract_number: Optional[str] = None
    invoice_number: Optional[str] = None
    version: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(OrderBase):
    """Schema for creating an order with optional product list."""

    products: Optional[List[ProductBase]] = None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(OrderBase):
    """Schema representing a single order."""

    id: int

    model_config = ConfigDict(from_attributes=True)
