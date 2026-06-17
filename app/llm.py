import json
import logging
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
)

SYSTEM_PROMPT = """\
Ты — ассистент службы поддержки клиентов. Твоя задача:
1. Классифицировать обращение по одной категории: billing, support, complaint, other.
2. Написать черновик ответа (1–6 предложений) — только по тому, что есть в тексте. Не обещай того, чего нет в исходных данных.
3. Оценить уверенность: high, medium, low.
4. Если данных мало, тон агрессивный или ситуация нестандартная — выставить confidence=low и escalate=true.

Отвечай СТРОГО в формате JSON (без markdown, без пояснений):
{
  "category": "billing|support|complaint|other",
  "draft_reply": "...",
  "confidence": "high|medium|low",
  "escalate": true|false
}
"""

FALLBACK_REPLY = (
    "Спасибо за обращение. Ваш запрос передан оператору и будет обработан в ближайшее время."
)


async def classify_ticket(text: str) -> dict:
    """Call LLM, parse result. On any error → escalate with fallback reply."""
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,
            max_tokens=512,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)

        # Validate required keys
        for key in ("category", "draft_reply", "confidence", "escalate"):
            if key not in result:
                raise ValueError(f"Missing key: {key}")

        # Clamp values to allowed sets
        if result["category"] not in ("billing", "support", "complaint", "other"):
            result["category"] = "other"
        if result["confidence"] not in ("high", "medium", "low"):
            result["confidence"] = "low"
        result["escalate"] = bool(result["escalate"])

        return result

    except Exception as exc:
        logger.error("LLM error: %s", exc)
        return {
            "category": "other",
            "draft_reply": FALLBACK_REPLY,
            "confidence": "low",
            "escalate": True,
            "error": str(exc),
        }
