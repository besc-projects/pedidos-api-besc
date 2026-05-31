from sqlalchemy import Column, String
from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "core"}

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)