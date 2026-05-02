"""APScheduler weekly mine job."""

import asyncio
import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from groq import Groq

from database import AsyncSessionLocal
from mining import mining_crawl

logger = logging.getLogger(__name__)


class WeeklyScheduler:
    def __init__(self, groq_client: Groq):
        self._groq = groq_client
        self._sched = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        self._sched.add_job(
            self._run_sync,
            trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
            id="weekly_hook_mining",
            replace_existing=True,
        )
        self._sched.start()
        logger.info("WeeklyScheduler started (Mon 09:00 UTC)")

    def shutdown(self, wait: bool = False) -> None:
        if getattr(self._sched, "running", False):
            self._sched.shutdown(wait=wait)
            logger.info("WeeklyScheduler shut down")

    def _run_sync(self) -> None:
        asyncio.run(self._run_async())

    async def _run_async(self) -> None:
        if not (os.getenv("GROQ_API_KEY") or "").strip():
            logger.warning("Weekly crawl skipped — GROQ_API_KEY not set")
            return
        categories = [
            "ecommerce",
            "marketing",
            "ai_tools",
            "startups",
            "photography",
            "content",
        ]
        limit = 30
        logger.info("Weekly crawl job started")
        try:
            async with AsyncSessionLocal() as db:
                result = await mining_crawl(db, self._groq, categories, limit)
                await db.commit()
                for h in result["hooks"]:
                    try:
                        await db.refresh(h)
                    except Exception:
                        logger.exception("Weekly refresh hook failed")
            logger.info(
                "Weekly crawl done posts_found=%s hooks_extracted=%s",
                result["posts_found"],
                result["hooks_extracted"],
            )
        except Exception:
            logger.exception("Weekly crawl job failed")
