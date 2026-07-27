from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    DateTime,
)
from sqlalchemy.sql import func
from app.db.base import Base


class HistoryProcess(Base):
    __tablename__ = "process_history"
    __table_args__ = {"schema": "audit"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, nullable=False)
    step = Column(String(80), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(10), nullable=False, server_default="info")
    created_by = Column(String(120), nullable=True)
    occurred_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Remove updated_at herdado da Base
    updated_at = None
