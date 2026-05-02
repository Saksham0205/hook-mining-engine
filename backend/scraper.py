import asyncio
from typing import Iterable, List

import feedparser
import httpx


DEFAULT_RSS_FEEDS = [
    "https://feeds.feedburner.com/entrepreneur/latest",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://www.producthunt.com/feed",
]

KEYWORD_CATEGORIES = [
    ("ecommerce", ["product", "amazon", "shopify", "brand", "conversion", "shop"]),
    ("marketing", ["marketing", "viral", "content", "hook", "copy", "audience"]),
    ("ai_tools", ["ai", "gpt", "llm", "automation", "claude", "openai"]),
    ("startups", ["startup", "founder", "mrr", "arr", "saas", "raise"]),
    ("photography", ["photo", "photography", "image", "shoot", "lifestyle"]),
    ("content", ["creator", "influencer", "youtube", "blog", "video"]),
]


def _assign_category(title: str, allowed: Iterable[str]) -> str | None:
    t = title.lower()
    for cat, kws in KEYWORD_CATEGORIES:
        if cat not in allowed:
            continue
        for kw in kws:
            if kw in t:
                return cat
    return None


def _dedupe_by_title(items: List[dict]) -> List[dict]:
    seen: set[str] = set()
    out: List[dict] = []
    for it in items:
        title = (it.get("title") or "").strip().lower()
        if not title or title in seen:
            continue
        seen.add(title)
        out.append(it)
    return out


async def scrape_hackernews(limit: int = 30) -> List[dict]:
    out: List[dict] = []
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        r = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        r.raise_for_status()
        ids = r.json()[:limit]
        for sid in ids:
            try:
                ir = await client.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                )
                ir.raise_for_status()
                item = ir.json()
                if not isinstance(item, dict):
                    continue
                title = item.get("title")
                score = item.get("score") or 0
                url = item.get("url") or ""
                if not title or score <= 50:
                    continue
                if not url:
                    url = f"https://news.ycombinator.com/item?id={sid}"
                out.append(
                    {
                        "title": title,
                        "url": url,
                        "score": score,
                        "source": "hackernews",
                    }
                )
            except httpx.HTTPError:
                continue
    return out


async def scrape_devto(limit: int = 20) -> List[dict]:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        r = await client.get(
            "https://dev.to/api/articles", params={"top": "7", "per_page": limit}
        )
        r.raise_for_status()
        data = r.json()
    out: List[dict] = []
    if not isinstance(data, list):
        return out
    for article in data:
        if not isinstance(article, dict):
            continue
        title = article.get("title")
        url = article.get("url")
        reactions = article.get("positive_reactions_count") or 0
        if title and url:
            out.append(
                {
                    "title": title,
                    "url": url,
                    "score": reactions,
                    "source": "devto",
                }
            )
    return out


async def scrape_rss(
    feeds: List[str] | None = None, limit: int = 20
) -> List[dict]:
    urls = feeds or DEFAULT_RSS_FEEDS
    out: List[dict] = []
    sem = asyncio.Semaphore(8)

    async def fetch_feed(url: str):
        async with sem:
            try:
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as c:
                    r = await c.get(url)
                    r.raise_for_status()
                    body = r.text
                parsed = feedparser.parse(body)
                entries = getattr(parsed, "entries", None) or []
                per = entries[:limit]
                for e in per:
                    title = getattr(e, "title", None)
                    link = getattr(e, "link", None)
                    if isinstance(e, dict):
                        title = title or e.get("title")
                        link = link or e.get("link")
                    if title and link:
                        out.append(
                            {
                                "title": str(title),
                                "url": str(link),
                                "score": 100,
                                "source": "rss",
                            }
                        )
            except Exception:
                return

    await asyncio.gather(*(fetch_feed(u) for u in urls))
    return out


async def scrape_all(categories: List[str], limit: int) -> List[dict]:
    raw_allowed = set(c.lower() for c in (categories or []))
    allowed = raw_allowed if raw_allowed else {
        "ecommerce",
        "marketing",
        "ai_tools",
        "startups",
        "photography",
        "content",
    }
    hn, dv, rss = await asyncio.gather(
        scrape_hackernews(30),
        scrape_devto(20),
        scrape_rss(None, limit=20),
    )
    merged = _dedupe_by_title(hn + dv + rss)
    filtered: List[dict] = []
    for row in merged:
        cat = _assign_category(row["title"], allowed)
        if cat is None:
            continue
        r = dict(row)
        r["category"] = cat
        filtered.append(r)
    filtered.sort(key=lambda x: x.get("score", 0), reverse=True)
    return filtered[:limit]


class MultiSourceScraper:
    async def scrape_hackernews(self, limit: int = 30) -> list[dict]:
        return await scrape_hackernews(limit)

    async def scrape_devto(self, limit: int = 20) -> list[dict]:
        return await scrape_devto(limit)

    async def scrape_rss(self, feeds: list[str] | None = None, limit: int = 20) -> list[dict]:
        return await scrape_rss(feeds, limit)

    async def scrape_all(self, categories: list[str], limit: int) -> list[dict]:
        return await scrape_all(categories, limit)
