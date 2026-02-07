from sqlalchemy import Column, String

from app.db.base import Base


class BaseStatus(Base):

    __abstract__ = True

    name = Column(String(255))
    description = Column(String(255))
