from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в Me Helper!\n\n"
        "Отправьте /new, затем пришлите фото товара с подписью или просто текст.\n"
        "Я улучшу текст, покажу результат и опубликую его только после подтверждения."
    )
