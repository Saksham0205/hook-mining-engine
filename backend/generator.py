import asyncio
import re
from typing import List

from groq import Groq

from models import HookPattern

MODEL = "llama-3.3-70b-versatile"

PLATFORM_RULES = {
    "Instagram": """- Max 60 words total
- 4-6 very short lines, one idea per line
- Aggressive line breaks — every line stands alone
- End with a hook question or 👇 CTA
- Use 1-2 emojis max, only where natural
- Write like a founder talking to a friend
- Specific numbers over vague claims""",
    "LinkedIn": """- Max 120 words total
- First line must stop the scroll — no context setting
- Short punchy paragraphs (2-3 lines max each)
- One concrete stat or specific number required
- End with a soft question CTA
- No hashtags
- Write like a confident operator, not a marketer""",
    "Twitter/X": """- Max 280 characters total
- First 5 words must hook immediately
- One single punchy idea only
- Specific and concrete — no fluff
- Optional: end with a question
- Zero hashtags""",
}

GOOD_EXAMPLES = {
    "Instagram": """EXAMPLE 1:
I used to pay $3,000 per photo shoot.

Now I get 50 lifestyle shots in 3 seconds.

Same brand. 10x the content. Zero photographer.

This is what Pixii does 👇

EXAMPLE 2:
Our return rate dropped 60% after we changed one thing.

Not the product.
Not the price.
Not the ads.

The photos.""",
    "LinkedIn": """EXAMPLE 1:
We cut our photography budget by 95%.

Not by lowering quality — by using AI.

Old process: Book photographer → shoot day → editing → 2 weeks → $3K
New process: Upload product → Pixii → 50 lifestyle photos → 3 seconds → $0

Our conversion rate went up, not down.

What's your current photography spend?

EXAMPLE 2:
I analyzed 47 product listings last month.

The ones converting above 8% had one thing in common.

Not price. Not reviews. Not copy.

Lifestyle photos showing the product in real context.

Studio shots convert at 2.3%. Lifestyle shots convert at 6.8%.

That's a 3x difference from one creative decision.""",
    "Twitter/X": """EXAMPLE 1:
Spent $3K on product photos last month.

Pixii does the same in 3 seconds.

We're not going back.

EXAMPLE 2:
Your product photo is your #1 salesperson.

Most brands treat it like an afterthought.""",
}


class PostGenerator:
    async def generate_posts(
        self,
        hook: HookPattern,
        topic: str,
        platform: str,
        groq_client: Groq,
    ) -> List[str]:
        system = """You are a viral social media writer for Pixii — an AI tool that generates lifestyle product photos for ecommerce brands instantly.

Your writing style:
- You write like a founder, not a marketer
- Short, punchy, direct sentences
- Specific numbers and concrete claims only
- You show, you don't tell
- Every line earns its place or gets cut
- You never use corporate speak

Pixii context (use these facts):
- Pixii generates lifestyle product photos in seconds using AI
- Replaces expensive photo shoots ($3K+ per shoot → $0)
- Ecommerce brands use it to get 50+ lifestyle shots instantly
- Lifestyle photos convert 3x better than white-background studio shots
- Used by DTC brands, Amazon sellers, Shopify stores
- Reduces return rates (better photos = accurate expectations)"""
        user = f"""Write 3 different {platform} posts for Pixii using this hook pattern.

Hook pattern: {hook.pattern}
Hook template: {hook.template}
Topic angle: {topic}

Platform rules for {platform}:
{PLATFORM_RULES.get(platform, PLATFORM_RULES["Instagram"])}

BANNED words/phrases — never use any of these:
"game-changer", "revolutionize", "seamlessly", "leverage", "utilize", "in today's world",
"unlock the power", "elevate your brand", "take your brand to the next level",
"discover the power", "innovative solution", "cutting-edge", "state-of-the-art",
"I'm excited to share", "transform your", "unprecedented"

Good examples to match the style:
{GOOD_EXAMPLES.get(platform, GOOD_EXAMPLES["Instagram"])}

Critical rules:
1. Open EVERY variation with the hook template filled in concretely
2. Each variation must take a completely different angle
3. Use specific numbers — never say "many", "significantly", "greatly"
4. Never mention any year
5. Separate each variation with exactly: ---

Write all 3 now. No preamble, no labels, just the posts separated by ---"""

        def _call():
            return groq_client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.85,
                max_tokens=2048,
            )

        completion = await asyncio.to_thread(_call)
        raw = completion.choices[0].message.content or ""
        print("[Groq generate_posts]", raw)

        parts = [p.strip() for p in raw.split("---") if p.strip()]
        cleaned: List[str] = []
        for p in parts:
            p = re.sub(r"^(?:\d+[\).\]]\s*|\*\s*|[-•]\s*)", "", p).strip()
            cleaned.append(p)
        if len(cleaned) < 3 and raw.strip():
            cleaned = [raw.strip()] if not cleaned else cleaned
        while len(cleaned) < 3:
            cleaned.append(cleaned[-1] if cleaned else "")
        return cleaned[:3]
