from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from config import CHANNEL_ID

MAX_MESSAGE_LENGTH = 4096
MAX_PHOTO_CAPTION_LENGTH = 1024


def _split_text(text: str, limit: int = MAX_MESSAGE_LENGTH) -> list[str]:
    chunks: list[str] = []
    current = ""

    for paragraph in text.split("\n"):
        candidate = f"{current}\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= limit:
            current = candidate
            continue

        if current:
            chunks.append(current)

        while len(paragraph) > limit:
            chunks.append(paragraph[:limit])
            paragraph = paragraph[limit:]

        current = paragraph

    if current:
        chunks.append(current)

    return chunks or [text[:limit]]


async def check_telegram_connection(bot: Bot):
    try:
        return await bot.get_me()
    except TelegramAPIError as exc:
        raise RuntimeError(
            "Не удалось подключиться к Telegram API. Проверьте BOT_TOKEN и доступ к Telegram."
        ) from exc


async def publish_post(bot: Bot, text: str, photo_file_id: str | None = None) -> None:
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Нельзя опубликовать пустой текст")

    try:
        if photo_file_id and len(clean_text) <= MAX_PHOTO_CAPTION_LENGTH:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo_file_id,
                caption=clean_text,
            )
            return

        if photo_file_id:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo_file_id)

        for chunk in _split_text(clean_text):
            await bot.send_message(chat_id=CHANNEL_ID, text=chunk)
    except TelegramAPIError as exc:
        raise RuntimeError(
            "Не удалось опубликовать пост в канал. Проверьте CHANNEL_ID и права бота в канале."
        ) from exc
