from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.products import ProductResponse, ProductBase


class OrderBase(BaseModel):
    vale_order_id: int
    status_id: int
    total_value: float
    portal: str
    center: str
    state: str
    cnpj: str
    days_to_delivery: Optional[str] = None
    proposal_id: Optional[int] = None
    besc_order_id: Optional[int] = None
    contract_number: Optional[str] = None
    invoice_number: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrderUpdater(BaseModel):
    status_id: int = Field(..., description="ID do novo status do pedido")


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
