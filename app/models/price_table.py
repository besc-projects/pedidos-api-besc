from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from app.db.base import Base


class PriceTable(Base):
    """Modelo da tabela de preços"""

    __tablename__ = "price_table"
    __table_args__ = (
        UniqueConstraint("pn", "destination", name="uq_price_table_pn_destination"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pn = Column(String, index=True, nullable=False)
    long_description = Column(String, nullable=False)
    description = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)

    def __repr__(self):
        return f"<PriceTable(pn={self.pn}, unit_price={self.unit_price})>"
