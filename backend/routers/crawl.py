import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from groq import Groq
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_db
from mining import mining_crawl
from schemas import CrawlBody, CrawlResponse, HookPatternRead, PostRead

logger = logging.getLogger(__name__)

router = APIRouter(tags=["crawl"])


def _groq(request: Request) -> Groq:
    g = request.app.state.groq
    if g is None:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY not configured. Copy .env.example to .env and set your key.",
        )
    return g


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_posts(
    body: CrawlBody,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    groq_client = _groq(request)
    try:
        result = await mining_crawl(db, groq_client, body.categories, body.limit)
        await db.commit()
        for h in result["hooks"]:
            try:
                await db.refresh(h)
            except Exception:
                logger.exception("Refresh hook failed after crawl")
    except HTTPException:
        raise
    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            logger.exception("Rollback failed during crawl rollback")
        detail = getattr(e, "message", None) or str(e)
        logger.exception("Crawl failed")
        raise HTTPException(status_code=500, detail=detail) from e

    posts_reads = [
        PostRead(
            title=p.get("title", "")[:2048],
            source=p.get("source", "")[:64],
            score=int(p.get("score") or 0),
            category=str(p.get("category", ""))[:128],
            url=(p.get("url") or "")[:4096],
        )
        for p in result["posts"]
    ]
    hooks_reads = [HookPatternRead.model_validate(h) for h in result["hooks"]]
    return CrawlResponse(
        posts_found=result["posts_found"],
        hooks_extracted=len(result["hooks"]),
        hooks=hooks_reads,
        posts=posts_reads,
    )
