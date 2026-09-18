from sqlalchemy import Column, Integer, BigInteger, String, Numeric, DateTime, func
from app.db.base import Base


class TaxReferenceProductSupra(Base):
    __tablename__ = "tax_references"
    __table_args__ = {"schema": "pricing"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_product = Column(Integer, nullable=False, index=True)

    ncm_code = Column(String(10), nullable=False)
    ipi = Column(Numeric(5, 2), nullable=True)
    icms = Column(Numeric(5, 2), nullable=True)
    icms_st = Column(Numeric(5, 2), nullable=True)
    origin = Column(String(50), nullable=True)

    # Snapshot do valor declarado na detecção (o "antes"), o vínculo com o
    # chamado que trata a divergência e quando ela foi resolvida.
    declared_ncm_code = Column(String(10), nullable=True)
    declared_ipi = Column(Numeric(5, 2), nullable=True)
    declared_icms = Column(Numeric(5, 2), nullable=True)
    declared_icms_st = Column(Numeric(5, 2), nullable=True)
    declared_origin = Column(String(50), nullable=True)
    ticket_id = Column(Integer, nullable=True, index=True)
    resolved_at = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )