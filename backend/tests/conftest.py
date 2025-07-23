# tests/conftest.py

import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from petfit.infra.database import Base
from petfit.api.main import app
from petfit.api import deps
from asgi_lifespan import LifespanManager

# URL para o banco de testes (deve bater com seu docker-compose)
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://test_user:test_password@db_test:5432/petfit_test",
)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Evita conflito de loops no pytest-asyncio."""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def setup_engine():
    """Cria engine e sessão de teste."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async_session = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    # Criação de tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine, async_session

    # Teardown: drop tables
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(setup_engine):
    """Cria uma sessão de banco por teste."""
    _, async_session = setup_engine
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(setup_engine):
    """Cria cliente de teste com override de dependências."""
    _, async_session = setup_engine

    async def override_get_db_session():
        async with async_session() as session:
            yield session

    app.dependency_overrides[deps.get_db_session] = override_get_db_session

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    app.dependency_overrides.clear()