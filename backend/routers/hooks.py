import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_db
from models import HookPattern, Post
from schemas import HookPatternRead, HooksListResponse, HooksStatsResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["hooks"])


@router.get("/hooks/stats", response_model=HooksStatsResponse)
async def hooks_stats(db: AsyncSession = Depends(get_db)):
    try:
        th = await db.scalar(select(func.count(HookPattern.id)))
        tp = await db.scalar(select(func.count(Post.id)))
        th = int(th or 0)
        tp = int(tp or 0)
        stmt = (
            select(HookPattern.category, func.count().label("c"))
            .group_by(HookPattern.category)
            .order_by(func.count().desc())
            .limit(8)
        )
        rows = (await db.execute(stmt)).all()
        top = [r[0] for r in rows if r and r[0]]
    except Exception as e:
        logger.exception("hooks stats DB error")
        raise HTTPException(status_code=500, detail=str(e)) from e

    return HooksStatsResponse(
        total_hooks=th,
        total_posts_crawled=tp,
        top_categories=top,
    )


@router.get("/hooks", response_model=HooksListResponse)
async def list_hooks(db: AsyncSession = Depends(get_db)):
    try:
        stmt = (
            select(HookPattern)
            .order_by(HookPattern.usage_count.desc(), HookPattern.created_at.desc())
        )
        rows = (await db.execute(stmt)).scalars().all()
    except Exception as e:
        logger.exception("list hooks DB error")
        raise HTTPException(status_code=500, detail=str(e)) from e

    return HooksListResponse(
        hooks=[HookPatternRead.model_validate(h) for h in rows],
        total=len(rows),
    )


@router.delete("/hooks/{hook_id}")
async def delete_hook(hook_id: int, db: AsyncSession = Depends(get_db)):
    try:
        hp = await db.get(HookPattern, hook_id)
        if not hp:
            raise HTTPException(status_code=404, detail="Hook not found")
        db.delete(hp)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            logger.exception("rollback on delete_hook")
        logger.exception("delete_hook DB error")
        raise HTTPException(status_code=500, detail=str(e)) from e
    return {"ok": True}
