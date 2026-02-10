from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Integer,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from app.db.base import Base


class HistoryProcess(Base):
    __tablename__ = "history_process"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    orders = Column(String(64), nullable=False)
    step = Column(String(20), nullable=False)
    id_situation = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Constraint para garantir que não exista id_situation duplicado para o mesmo step na mesma orders
    __table_args__ = (
        UniqueConstraint(
            "orders", "step", "id_situation", name="uq_orders_step_situation"
        ),
    )

    # Remove updated_at herdado da Base
    updated_at = None
