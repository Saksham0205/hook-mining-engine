import asyncio
import json
import logging
import re
from typing import Any, List

from groq import Groq

logger = logging.getLogger(__name__)

MODEL = "llama-3.3-70b-versatile"


def _strip_json_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\s*```\s*$", "", t)
    return t.strip()


class HookAnalyzer:
    async def extract_hooks(self, posts: List[dict], groq_client: Groq) -> List[dict]:
        if not posts:
            return []

        lines = [
            f"{i + 1}. [{row.get('source', '?')}] {row.get('title', '')}".strip()
            for i, row in enumerate(posts[:80])
            if row.get("title")
        ]
        body = "\n".join(lines)
        n = len(lines)

        system = (
            "You are a viral content strategist. Extract reusable hook frameworks from "
            "viral content. Return only valid JSON."
        )
        user_prompt = f"""Analyze these {n} viral post titles. Extract 8 distinct reusable hook patterns.

Posts:
{body}

Return ONLY a valid JSON array (no markdown, no explanation):
[{{
  "pattern": "short descriptive name (3-4 words)",
  "template": "reusable template — use [TOPIC] and [NUMBER] as placeholders",
  "example": "closest matching title from above",
  "category": "curiosity|pain|number|story|controversy|transformation|social_proof",
  "strength": "high|medium"
}}]"""

        def _call():
            return groq_client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.55,
                max_tokens=4096,
            )

        completion = await asyncio.to_thread(_call)
        raw = completion.choices[0].message.content or ""
        print("[Groq extract_hooks]", raw)
        cleaned = _strip_json_fences(raw)

        hooks: Any
        try:
            hooks = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.exception("Groq hook JSON parse failed; raw excerpt: %s", raw[:800])
            return []

        if not isinstance(hooks, list):
            return []

        seen: set[str] = set()
        out: List[dict] = []
        for h in hooks:
            if not isinstance(h, dict):
                continue
            name = str(h.get("pattern", "") or "").strip().lower()
            if not name or name in seen:
                continue
            seen.add(name)
            out.append(
                {
                    "pattern": str(h.get("pattern", "")).strip(),
                    "template": str(h.get("template", "")).strip(),
                    "example": str(h.get("example", "")).strip(),
                    "category": str(h.get("category", "curiosity")).strip(),
                    "strength": str(h.get("strength", "medium")).strip(),
                }
            )
            if len(out) >= 8:
                break
        return out
