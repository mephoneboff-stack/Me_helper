from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("new"))
async def new_post(message: Message):
    await message.answer(
        "📷 Отправьте фотографию товара с подписью.\n\n"
        "После этого я улучшу текст с помощью AI."
    )


@router.message()
async def receive_post(message: Message):
    if message.photo:
        await message.answer(
            "✅ Фото получено.\n\n"
            "Следующий шаг — отправим текст в AI."
        )