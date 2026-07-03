from openai import AsyncOpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL


SYSTEM_PROMPT = (
    "Ты редактор Telegram-канала. Улучши текст публикации на русском языке: "
    "сделай его ясным, аккуратным и продающим, но не выдумывай факты, цены, "
    "характеристики, скидки или условия. Сохрани смысл исходного текста."
)


async def edit_text(text: str) -> str:
    source_text = text.strip()
    if not source_text:
        raise ValueError("Текст для AI-редактирования пустой")

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY не задан в .env")

    async with AsyncOpenAI(api_key=OPENAI_API_KEY) as client:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": source_text},
            ],
            temperature=0.4,
        )

    edited_text = response.choices[0].message.content
    if not edited_text:
        raise RuntimeError("AI вернул пустой ответ")

    return edited_text.strip()
