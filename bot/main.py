import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN
from handlers.post import router as post_router

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
dp.include_router(post_router)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в Me Helper!\n\n"
        "Отправьте мне фотографию товара и текст.\n"
        "Я улучшу текст, покажу результат и после вашего подтверждения опубликую его."
    )


async def main():
    print("✅ Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())