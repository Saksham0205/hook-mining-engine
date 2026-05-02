import os
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models import Base

_BACKEND_DIR = Path(__file__).resolve().parent
_db_path = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{(_BACKEND_DIR / 'hook_engine.db').as_posix()}",
)
if _db_path.startswith("sqlite:///"):
    _db_path = _db_path.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

connect_args = {}
engine_kwargs = {"echo": False}
if "+aiosqlite" in (_db_path or ""):
    connect_args["check_same_thread"] = False
    engine_kwargs["connect_args"] = connect_args

engine = create_async_engine(_db_path, **engine_kwargs)


@event.listens_for(engine.sync_engine, "connect")
def _sqlite_pragma(dbapi_connection, _connection_record):
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