from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.schemas.products import ProductResponse


class TaxReferenceBase(BaseModel):
    id_product: int = Field(..., description="ID do produto")
    ncm_code: str = Field(..., description="Código NCM do produto", max_length=10)
    ipi: Optional[Decimal] = Field(None, description="Alíquota IPI (%)")
    icms: Optional[Decimal] = Field(None, description="Alíquota ICMS (%)")
    icms_st: Optional[Decimal] = Field(None, description="Alíquota ICMS-ST (%)")
    origin: Optional[str] = Field(None, description="Origem do produto", max_length=50)

    model_config = ConfigDict(from_attributes=True)


class TaxReferenceCreate(TaxReferenceBase):
    """Schema para criar uma referência fiscal de produto supra"""

    pass


class TaxReferenceUpdate(BaseModel):
    """Schema para atualizar uma referência fiscal — todos os campos são opcionais"""

    id_product: Optional[int] = Field(None, description="ID do produto")
    ncm_code: Optional[str] = Field(None, description="Código NCM do produto", max_length=10)
    ipi: Optional[Decimal] = Field(None, description="Alíquota IPI (%)")
    icms: Optional[Decimal] = Field(None, description="Alíquota ICMS (%)")
    icms_st: Optional[Decimal] = Field(None, description="Alíquota ICMS-ST (%)")
    origin: Optional[str] = Field(None, description="Origem do produto", max_length=50)

    model_config = ConfigDict(from_attributes=True)


class TaxReferenceResponse(TaxReferenceBase):
    """Schema de resposta para referência fiscal de produto supra"""

    id: int = Field(..., description="ID do registro")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")

    model_config = ConfigDict(from_attributes=True)


class ProductTaxReferenceResponse(BaseModel):
    """Schema de resposta combinada para produto e referência fiscal."""

    product: ProductResponse
    tax_reference: TaxReferenceResponse

    model_config = ConfigDict(from_attributes=True)
