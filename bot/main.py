import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, ErrorEvent

from config import BOT_TOKEN
from handlers.language import router as language_router
from handlers.post import router as post_router
from handlers.start import router as start_router
from services.scheduler_service import run_scheduler
from services.telegram_service import check_telegram_connection

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(language_router)
    dp.include_router(post_router)

    @dp.error()
    async def on_error(event: ErrorEvent):
        logging.exception("Необработанная ошибка в хендлере: %s", event.exception)

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

        scheduler_task = asyncio.create_task(run_scheduler(bot))
        try:
            await dp.start_polling(bot)
        finally:
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                pass
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
