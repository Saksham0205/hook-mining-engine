from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HookPatternRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pattern: str
    template: str
    example: str
    category: str
    strength: str
    usage_count: int = 0
    created_at: datetime | None = None


class CrawlBody(BaseModel):
    categories: list[str]
    limit: int


class PostRead(BaseModel):
    title: str
    source: str
    score: int
    category: str
    url: str


class CrawlResponse(BaseModel):
    posts_found: int
    hooks_extracted: int
    hooks: list[HookPatternRead]
    posts: list[PostRead]


class HooksListResponse(BaseModel):
    hooks: list[HookPatternRead]
    total: int


class HooksStatsResponse(BaseModel):
    total_hooks: int
    total_posts_crawled: int
    top_categories: list[str]


class GenerateBody(BaseModel):
    hook_id: int
    topic: str
    platform: str


class GenerateResponse(BaseModel):
    variations: list[str]
    hook: HookPatternRead


class HealthResponse(BaseModel):
    status: str
    hooks_count: int


class PingResponse(BaseModel):
    status: str = "ok"
