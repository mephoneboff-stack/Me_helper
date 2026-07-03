import asyncio
import sys
from pathlib import Path

from aiogram import Bot

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent / "bot"))

from config import BOT_TOKEN, CHANNEL_ID
from services.telegram_service import check_telegram_connection


async def main():
    bot = Bot(BOT_TOKEN)

    try:
        me = await check_telegram_connection(bot)
        chat = await bot.get_chat(CHANNEL_ID)
        print(f"Telegram API подключен: @{me.username}")
        print(f"Канал найден: {chat.title or chat.id}")
    except Exception as e:
        print("Ошибка:", e)
    finally:
        await bot.session.close()


asyncio.run(main())
