# app/models/status/orders_status.py
from app.models.status.base import BaseStatus


class OrdersStatus(BaseStatus):
    __tablename__ = "orders_status"
