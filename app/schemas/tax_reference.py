from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class TaxReferenceBase(BaseModel):
    id_product: int = Field(..., description="ID do produto")
    ncm_code: str = Field(..., description="Código NCM do produto", max_length=10)
    ipi: Optional[Decimal] = Field(None, description="Alíquota IPI (%)")
    icms: Optional[Decimal] = Field(None, description="Alíquota ICMS (%)")
    icms_st: Optional[Decimal] = Field(None, description="Alíquota ICMS-ST (%)")
    origin: Optional[str] = Field(None, description="Origem do produto", max_length=50)
    declared_ncm_code: Optional[str] = Field(None, description="NCM declarado no pedido", max_length=10)
    declared_ipi: Optional[Decimal] = Field(None, description="IPI declarado (%)")
    declared_icms: Optional[Decimal] = Field(None, description="ICMS declarado (%)")
    declared_icms_st: Optional[Decimal] = Field(None, description="ICMS-ST declarado (%)")
    declared_origin: Optional[str] = Field(None, description="Origem declarada", max_length=50)
    ticket_id: Optional[int] = Field(None, description="Chamado que trata a divergência")
    resolved_at: Optional[datetime] = Field(None, description="Quando a divergência foi resolvida")

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
    declared_ncm_code: Optional[str] = Field(None, description="NCM declarado no pedido", max_length=10)
    declared_ipi: Optional[Decimal] = Field(None, description="IPI declarado (%)")
    declared_icms: Optional[Decimal] = Field(None, description="ICMS declarado (%)")
    declared_icms_st: Optional[Decimal] = Field(None, description="ICMS-ST declarado (%)")
    declared_origin: Optional[str] = Field(None, description="Origem declarada", max_length=50)
    ticket_id: Optional[int] = Field(None, description="Chamado que trata a divergência")
    resolved_at: Optional[datetime] = Field(None, description="Quando a divergência foi resolvida")

    model_config = ConfigDict(from_attributes=True)


class TaxReferenceResponse(TaxReferenceBase):
    """Schema de resposta para referência fiscal de produto supra"""

    id: int = Field(..., description="ID do registro")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")

    model_config = ConfigDict(from_attributes=True)
