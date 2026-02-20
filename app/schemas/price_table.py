from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class PriceTableBase(BaseModel):
    """Schema base para tabela de preços"""

    pn: str = Field(..., description="Part Number (PN) do produto", min_length=1)
    long_description: str = Field(
        ..., description="Descrição longa do produto", min_length=1
    )
    description: str = Field(..., description="Descrição do produto", min_length=1)
    destination: str = Field(
        ..., description="Destino do produto [MG ou PA]", min_length=1
    )
    unit_price: float = Field(..., description="Preço unitário", gt=0)
    model_config = ConfigDict(from_attributes=True)


class PriceTableCreate(PriceTableBase):
    """Schema para criar uma entrada na tabela de preços"""

    pass


class PriceTableUpdate(BaseModel):
    """Schema para atualizar uma entrada na tabela de preços"""

    long_description: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, min_length=1)
    destination: Optional[str] = Field(None, min_length=1)
    unit_price: Optional[float] = Field(None, gt=0)
    model_config = ConfigDict(from_attributes=True)


class PriceTableResponse(PriceTableBase):
    """Schema de resposta para tabela de preços"""

    id: int = Field(..., description="ID do registro")

    model_config = ConfigDict(from_attributes=True)


class PriceByPNResponse(BaseModel):
    """Schema de resposta para consulta de preço por PN"""

    pn: str = Field(..., description="Part Number (PN) do produto")
    unit_price: float = Field(..., description="Preço unitário")
    description: str = Field(..., description="Descrição do produto")
    destination: str = Field(..., description="Destino do produto [MG ou PA]")
    model_config = ConfigDict(from_attributes=True)
