from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from app.db.base import Base


class HistoryProcess(Base):
    __tablename__ = "process_history"
    __table_args__ = (
        UniqueConstraint(
            "order_id", "description",
            name="uq_audit_process_history_order_description",
        ),
        {"schema": "audit"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, nullable=False)
    step = Column(String(80), nullable=False)
    # Único junto com order_id (uq_audit_process_history_order_description) —
    # 400 cobre o maior valor real hoje (80 chars) com folga; VARCHAR(MAX)
    # não pode ser indexado no SQL Server.
    description = Column(String(400), nullable=False)
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
