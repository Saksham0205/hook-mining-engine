"""Shared crawl pipeline for API and weekly scheduler."""

import logging
from typing import Any

from groq import Groq
from sqlalchemy import select

from analyzer import HookAnalyzer
from models import HookPattern, Post
from scraper import MultiSourceScraper

logger = logging.getLogger(__name__)


async def mining_crawl(
    db: Any, groq: Groq, categories: list[str], limit: int
) -> dict:
    scraper = MultiSourceScraper()
    analyzer = HookAnalyzer()
    posts_data = await scraper.scrape_all(categories, limit)

    for row in posts_data:
        try:
            url = (row.get("url") or "")[:4096]
            if not url:
                continue
            existing = await db.execute(select(Post.id).where(Post.url == url).limit(1))
            if existing.scalar_one_or_none():
                continue
            db.add(
                Post(
                    title=(row.get("title") or "")[:2048],
                    source=(row.get("source") or "unknown")[:64],
                    url=url,
                    score=int(row.get("score") or 0),
                    category=(str(row.get("category") or ""))[:128],
                )
            )
        except Exception:
            logger.exception("Failed to save crawled post to DB")

    hooks_list = await analyzer.extract_hooks(posts_data, groq)
    added: list[HookPattern] = []

    for h in hooks_list:
        try:
            pat = (h.get("pattern") or "").strip()
            if not pat:
                continue
            q = await db.execute(
                select(HookPattern).where(HookPattern.pattern == pat).limit(1)
            )
            if q.scalar_one_or_none():
                continue
            hp = HookPattern(
                pattern=pat[:512],
                template=h.get("template") or "",
                example=h.get("example") or "",
                category=(h.get("category") or "curiosity")[:64],
                strength=(h.get("strength") or "medium")[:32],
                usage_count=0,
            )
            db.add(hp)
            added.append(hp)
        except Exception:
            logger.exception("Failed to upsert hook pattern")

    try:
        await db.flush()
    except Exception:
        logger.exception("DB flush failed after mining_crawl inserts")

    return {
        "posts_found": len(posts_data),
        "hooks_extracted": len(added),
        "hooks": added,
        "posts": posts_data,
    }
