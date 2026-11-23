"""Async SQLAlchemy engine, session factory and Base."""

from collections.abc import AsyncIterator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Explicit package marker so ``import app.db`` works even when the package dir
# does not contain __init__.py.
__path__ = [__file__.rpartition("/")[0] or "."]
__all__ = ["Base"]


settings = get_settings()

engine_kwargs: dict = {"pool_pre_ping": True}
if "sqlite" in settings.DATABASE_URL:
    from sqlalchemy.pool import NullPool, StaticPool

    engine_kwargs["connect_args"] = {"check_same_thread": False}
    if settings.DATABASE_URL.endswith(":memory:") or settings.DATABASE_URL in {
        "sqlite+aiosqlite://",
        "sqlite+aiosqlite:///:memory:",
    }:
        engine_kwargs["poolclass"] = StaticPool
    else:
        # File-backed SQLite is safe across test event loops only when each
        # loop gets its own DBAPI connection.
        engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a database session."""
    async with async_session_factory() as session:
        yield session
