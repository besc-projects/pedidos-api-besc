from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from app.db.base import Base


from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from app.db.base import Base


class PriceTable(Base):
    __tablename__ = "prices"

    __table_args__ = (
        UniqueConstraint(
            "pn",
            "destination",
            name="uq_price_table_pn_destination"
        ),
        {"schema": "pricing"},
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pn = Column(String, index=True, nullable=False)
    long_description = Column(String, nullable=False)
    description = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)

    def __repr__(self):
        return (
            f"<PriceTable(pn={self.pn}, "
            f"unit_price={self.unit_price})>"
        )