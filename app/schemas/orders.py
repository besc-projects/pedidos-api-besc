from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.products import ProductResponse, ProductBase


class OrderBase(BaseModel):
    vale_order_id: int
    ticket_id: Optional[int] = None
    status_id: int
    total_value: float
    portal: str
    center: str
    state: str
    cnpj: str
    date: datetime
    days_to_delivery: Optional[str] = None
    proposal_id: Optional[int] = None
    besc_order_id: Optional[int] = None
    contract_number: Optional[str] = None
    invoice_number: Optional[str] = None
    version: Optional[int] = None
    ipi: Optional[float] = None
    icms: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrderUpdater(BaseModel):
    status_id: int = Field(..., description="ID do novo status do pedido")


class OrderUpdate(BaseModel):
    """Schema for partial order updates - all fields optional."""

    status_id: Optional[int] = None
    ticket_id: Optional[int] = None
    total_value: Optional[float] = None
    portal: Optional[str] = None
    center: Optional[str] = None
    state: Optional[str] = None
    cnpj: Optional[str] = None
    date: Optional[datetime] = None
    days_to_delivery: Optional[str] = None
    proposal_id: Optional[int] = None
    besc_order_id: Optional[int] = None
    contract_number: Optional[str] = None
    invoice_number: Optional[str] = None
    version: Optional[int] = None
    ipi: Optional[float] = None
    icms: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(OrderBase):
    """Schema for creating an order with optional product list."""

    products: Optional[List[ProductBase]] = None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(OrderBase):
    """Schema representing a single order."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class OrderWithProducts(OrderResponse):
    """Schema that includes related products."""

    products: List[ProductResponse] = []

    model_config = ConfigDict(from_attributes=True)
