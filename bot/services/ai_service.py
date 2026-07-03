from openai import AsyncOpenAI
from openai import AuthenticationError, OpenAIError

from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


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

    client_kwargs = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        client_kwargs["base_url"] = OPENAI_BASE_URL

    try:
        async with AsyncOpenAI(**client_kwargs) as client:
            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": source_text},
                ],
                temperature=0.4,
            )
    except AuthenticationError as exc:
        raise RuntimeError(
            "AI API отклонил ключ. Проверьте OPENAI_API_KEY, OPENAI_BASE_URL и OPENAI_MODEL в .env."
        ) from exc
    except OpenAIError as exc:
        raise RuntimeError(f"AI API временно недоступен: {exc.__class__.__name__}") from exc

    edited_text = response.choices[0].message.content
    if not edited_text:
        raise RuntimeError("AI вернул пустой ответ")

    return edited_text.strip()
