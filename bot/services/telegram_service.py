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


_SEND_METHODS = {
    "photo": "send_photo",
    "video": "send_video",
    "animation": "send_animation",
    "document": "send_document",
}

_MEDIA_CAPTION_LIMITS = {
    "photo": MAX_PHOTO_CAPTION_LENGTH,
    "video": MAX_PHOTO_CAPTION_LENGTH,
    "animation": MAX_PHOTO_CAPTION_LENGTH,
    "document": MAX_PHOTO_CAPTION_LENGTH,
}


async def publish_post(
    bot: Bot,
    text: str,
    media_type: str | None = None,
    file_id: str | None = None,
) -> None:
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Нельзя опубликовать пустой текст")

    if not media_type or not file_id:
        # Без вложения — просто текст
        try:
            for chunk in _split_text(clean_text):
                await bot.send_message(chat_id=CHANNEL_ID, text=chunk)
        except TelegramAPIError as exc:
            raise RuntimeError(
                "Не удалось опубликовать пост в канал. Проверьте CHANNEL_ID и права бота."
            ) from exc
        return

    method_name = _SEND_METHODS.get(media_type)
    if not method_name:
        # Неизвестный тип — отправляем как документ
        method_name = "send_document"

    caption_limit = _MEDIA_CAPTION_LIMITS.get(media_type, MAX_PHOTO_CAPTION_LENGTH)
    send_method = getattr(bot, method_name)

    try:
        if len(clean_text) <= caption_limit:
            await send_method(
                chat_id=CHANNEL_ID,
                **{_media_field(media_type): file_id},
                caption=clean_text,
            )
            return

        # Текст длиннее лимита подписи — отправляем вложение отдельно, текст сообщениями
        await send_method(
            chat_id=CHANNEL_ID,
            **{_media_field(media_type): file_id},
        )
        for chunk in _split_text(clean_text):
            await bot.send_message(chat_id=CHANNEL_ID, text=chunk)
    except TelegramAPIError as exc:
        raise RuntimeError(
            "Не удалось опубликовать пост в канал. Проверьте CHANNEL_ID и права бота в канале."
        ) from exc


def _media_field(media_type: str) -> str:
    """Возвращает имя параметра для метода send_* (photo/video/animation/document)."""
    return media_type if media_type != "animation" else "animation"
