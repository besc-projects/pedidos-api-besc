from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base


class PriceTable(Base):
    """Modelo da tabela de preços"""

    __tablename__ = "price_table"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pn = Column(String, unique=True, index=True, nullable=False)
    long_description = Column(String, nullable=False)
    description = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)

    def __repr__(self):
        return f"<PriceTable(pn={self.pn}, unit_price={self.unit_price})>"
