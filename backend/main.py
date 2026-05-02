import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import init_db
from deps import get_db
from models import HookPattern
from routers import crawl as crawl_router
from routers import generate as generate_router
from routers import hooks as hooks_router
from scheduler import WeeklyScheduler
from schemas import HealthResponse, PingResponse

load_dotenv(Path(__file__).resolve().parent / ".env")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

_scheduler: WeeklyScheduler | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    await init_db()
    api_key = (os.getenv("GROQ_API_KEY") or "").strip()
    app.state.groq = Groq(api_key=api_key) if api_key else None

    if api_key:
        _scheduler = WeeklyScheduler(app.state.groq)
        _scheduler.start()
    else:
        logger.warning("GROQ_API_KEY missing — AI routes will return 503 until configured")
    try:
        yield
    finally:
        if _scheduler is not None:
            _scheduler.shutdown(wait=False)
            _scheduler = None


app = FastAPI(title="Pixii Hook Mining Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crawl_router.router, prefix="/api")
app.include_router(hooks_router.router, prefix="/api")
app.include_router(generate_router.router, prefix="/api")


@app.get("/api/ping", response_model=PingResponse)
async def ping():
    """No database access — stable for uptime monitors / keep-alive cron jobs."""
    return PingResponse()


@app.get("/api/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)):
    try:
        hooks_count_raw = await db.scalar(select(func.count(HookPattern.id)))
        hooks_count = int(hooks_count_raw or 0)
    except Exception:
        logger.exception("health DB lookup failed")
        hooks_count = 0
    return HealthResponse(status="ok", hooks_count=hooks_count)


@app.get("/")
async def root():
    return {
        "service": "hook-mining-engine",
        "docs": "/docs",
        "keepalive_ping": "/api/ping",
        "health_with_db": "/api/health",
    }
