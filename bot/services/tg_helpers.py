import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message

logger = logging.getLogger(__name__)


async def safe_edit_text(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Редактирует текст сообщения, игнорируя 'message is not modified'.

    Telegram возвращает Bad Request, если новое содержимое совпадает со старым
    (например, пользователь повторно нажал уже выбранную кнопку). В этом случае
    нет смысла падать — состояние уже корректно.
    """
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "not modified" in str(exc):
            return
        raise
