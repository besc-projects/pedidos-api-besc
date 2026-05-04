from sqlalchemy import Column, Integer, BigInteger, String, Numeric, TIMESTAMP, func
from app.db.base import Base


class TaxReferenceProductSupra(Base):
    """Modelo da tabela de referência fiscal de produtos supra"""

    __tablename__ = "tax_reference_product_supra"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_product = Column(Integer, nullable=False, index=True)

    ncm_code = Column(String(10), nullable=False)
    ipi = Column(Numeric(5, 2), nullable=True)
    icms = Column(Numeric(5, 2), nullable=True)
    icms_st = Column(Numeric(5, 2), nullable=True)
    origin = Column(String(50), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<TaxReferenceProductSupra(id={self.id}, id_product={self.id_product}, ncm_code={self.ncm_code})>"
