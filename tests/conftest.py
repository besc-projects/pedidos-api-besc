"""Shared test fixtures.

Integration tests run against a throwaway in-memory SQLite database created
fresh for each test, so nothing is ever written to the real database. Postgres
schemas (``core``, ``support`` ...) are collapsed onto SQLite's single database
via ``schema_translate_map``.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import BigInteger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  # register all ORM models on the metadata
from app.core.security import create_access_token
from app.database import get_db
from app.db.base import Base
from app.main import app


@compiles(BigInteger, "sqlite")
def _compile_biginteger_as_integer_on_sqlite(type_, compiler, **kw):
    """SQLite only autoincrements INTEGER PRIMARY KEY, not BIGINT.

    Render BigInteger as INTEGER for the SQLite test database so autoincrement
    primary keys behave like they do on Postgres. Production is unaffected.
    """
    return "INTEGER"

# Map every Postgres schema used by the models to SQLite's default database.
SCHEMA_TRANSLATE_MAP = {
    table.schema: None for table in Base.metadata.tables.values() if table.schema
}


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide a session on a fresh in-memory SQLite database, discarded after."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        execution_options={"schema_translate_map": SCHEMA_TRANSLATE_MAP},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session = AsyncSession(engine, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Authenticated HTTP client bound to the ephemeral SQLite session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token("integration-tester")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as http_client:
        yield http_client
    app.dependency_overrides.clear()
