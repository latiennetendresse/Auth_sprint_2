from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import text

from settings import settings

Base = declarative_base()

engine = create_async_engine(
    settings.postgres_dsn, echo=settings.postgres_echo, future=True
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
async def db() -> AsyncSession:
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
async def db_truncate(db: AsyncSession):
    """Чистит Postgres перед каждым тестом."""
    for table in ["users", "sessions", "roles", "user_roles"]:
        await db.execute(text(f"TRUNCATE {table} CASCADE"))
    await db.commit()


@pytest.fixture
async def db_delete(db: AsyncSession):
    async def inner(table: str, id: str):
        await db.execute(
            text(f"DELETE FROM {table} WHERE id=:id").bindparams(id=id)  # noqa: S608
        )
        await db.commit()

    return inner


@pytest.fixture
async def admin_role(db: AsyncSession) -> dict:
    role_id = str(uuid4())
    await db.execute(
        text("INSERT INTO roles (id,name) VALUES(:id,'admin')").bindparams(id=role_id)
    )
    await db.commit()
    return {"id": role_id, "name": "admin"}


@pytest.fixture
async def add_role(db: AsyncSession):
    async def inner(user_id: str, role_id: str):
        await db.execute(
            text(
                "INSERT INTO user_roles (id,user_id,role_id) "
                "VALUES(:id,:user_id,:role_id)"
            ).bindparams(id=uuid4(), user_id=user_id, role_id=role_id)
        )
        await db.commit()

    return inner
