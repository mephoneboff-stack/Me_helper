from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.language import language_keyboard
from services.language_service import get_user_language, t

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    language = get_user_language(message.from_user.id if message.from_user else None)
    await message.answer(
        t("start", language),
        reply_markup=language_keyboard(language),
    )
