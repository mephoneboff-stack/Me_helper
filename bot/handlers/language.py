from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.language import LANGUAGE_CALLBACK_PREFIX, language_keyboard
from services.language_service import get_user_language, set_user_language, t
from services.tg_helpers import safe_edit_text

router = Router()


@router.message(Command("language"))
async def language_menu(message: Message):
    language = get_user_language(message.from_user.id if message.from_user else None)
    await message.answer(
        t("language_prompt", language),
        reply_markup=language_keyboard(language),
    )


@router.callback_query(F.data.startswith(LANGUAGE_CALLBACK_PREFIX))
async def set_language(callback: CallbackQuery):
    if not callback.from_user or not callback.data:
        await callback.answer()
        return

    language = callback.data.removeprefix(LANGUAGE_CALLBACK_PREFIX)
    language = set_user_language(callback.from_user.id, language)
    message_key = "language_ru_selected" if language == "ru" else "language_uz_selected"

    await safe_edit_text(
        callback.message,
        t(message_key, language),
        reply_markup=language_keyboard(language),
    )
    await callback.answer()
