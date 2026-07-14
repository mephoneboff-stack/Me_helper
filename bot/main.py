import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers.language import router as language_router
from handlers.post import router as post_router
from handlers.start import router as start_router
from services.telegram_service import check_telegram_connection

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(language_router)
    dp.include_router(post_router)

    try:
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Запуск"),
                BotCommand(command="language", description="Рус / Узб"),
                BotCommand(command="new", description="Новая публикация"),
                BotCommand(command="cancel", description="Отмена"),
            ]
        )
        me = await check_telegram_connection(bot)
        logging.info("Бот запущен: @%s", me.username)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
