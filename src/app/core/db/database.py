from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.config import settings


class Base(DeclarativeBase, MappedAsDataclass):
    pass

DATABASE_URI = settings.DB_URI
DATABASE_PREFIX = settings.DB_PREFIX


async_engine = create_async_engine(
    url=DATABASE_URI,
    future=True
)

async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session