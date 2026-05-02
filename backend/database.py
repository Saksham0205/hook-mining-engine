import os
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models import Base

_BACKEND_DIR = Path(__file__).resolve().parent


def _normalize_async_database_url(url: str) -> str:
    """Render/Heroku use postgres://… or postgresql://…; SQLAlchemy async wants postgresql+asyncpg://…"""
    u = url.strip()
    if not u:
        return u
    if u.startswith("sqlite:///"):
        return u.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    scheme, sep, rest = u.partition("://")
    if not sep:
        return u
    if scheme.startswith("postgresql+") and "asyncpg" in scheme:
        return u
    if scheme in ("postgres", "postgresql"):
        return f"postgresql+asyncpg://{rest}"
    return u


_database_url = _normalize_async_database_url(
    os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{(_BACKEND_DIR / 'hook_engine.db').as_posix()}"),
)

engine_kwargs = {"echo": False}
if "+aiosqlite" in _database_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(_database_url, **engine_kwargs)


@event.listens_for(engine.sync_engine, "connect")
def _sqlite_pragma(dbapi_connection, _connection_record):
    if engine.dialect.name != "sqlite":
        return
    try:
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()
    except Exception:
        pass


AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)