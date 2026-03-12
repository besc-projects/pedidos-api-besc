# app/database.py
import os
from dotenv import load_dotenv

load_dotenv()

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
from app.db.base import Base  # DeclarativeBase centralizado
from sqlalchemy.orm import configure_mappers


# ================================
# CONFIGURAÇÃO: URL & Engine
# ================================
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)
ECHO_SQL = os.getenv("ECHO_SQL", "true").lower() == "true"


engine = create_async_engine(DATABASE_URL, echo=ECHO_SQL, future=True, connect_args={})

# ================================
# SESSION FACTORY
# ================================
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# ================================
# DEPENDÊNCIA: get_db
# ================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ================================
# CONTEXTO MANUAL (fora do FastAPI)
# ================================
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ================================
# CRIAÇÃO DE TABELAS
# ================================
async def init_db():
    configure_mappers()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
