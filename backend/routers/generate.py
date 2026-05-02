import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from groq import Groq
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_db
from generator import PostGenerator
from models import GeneratedPost, HookPattern
from schemas import GenerateBody, GenerateResponse, HookPatternRead

logger = logging.getLogger(__name__)

router = APIRouter(tags=["generate"])


def _groq(request: Request) -> Groq:
    g = request.app.state.groq
    if g is None:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY not configured. Copy .env.example to .env and set your key.",
        )
    return g


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    body: GenerateBody,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    groq_client = _groq(request)
    gen = PostGenerator()

    try:
        stmt = select(HookPattern).where(HookPattern.id == body.hook_id)
        hook = (await db.execute(stmt)).scalar_one_or_none()
        if not hook:
            raise HTTPException(status_code=404, detail="Hook pattern not found")

        try:
            variations = await gen.generate_posts(
                hook, body.topic, body.platform, groq_client
            )
        except Exception as e:
            detail = getattr(e, "message", None) or str(e)
            logger.exception("Groq generate failed")
            raise HTTPException(status_code=500, detail=detail) from e

        for text in variations:
            try:
                db.add(
                    GeneratedPost(
                        hook_pattern_id=hook.id,
                        topic=body.topic[:512],
                        platform=body.platform[:64],
                        content=text,
                    )
                )
            except Exception:
                logger.exception("Saving GeneratedPost failed")

        try:
            hook.usage_count = int(hook.usage_count or 0) + 1
        except Exception:
            hook.usage_count = 1

        await db.commit()
        await db.refresh(hook)
    except HTTPException:
        raise
    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            logger.exception("Rollback during generate failed")
        logger.exception("Generate DB transaction failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

    return GenerateResponse(
        variations=variations,
        hook=HookPatternRead.model_validate(hook),
    )
