import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

import services.repost_store as store
from config import SCHEDULER_TICK_SECONDS, TZ_TASHKENT
from services.telegram_service import publish_post

logger = logging.getLogger(__name__)


async def run_scheduler(bot: Bot) -> None:
    """Фоновый цикл: раз в SCHEDULER_TICK_SECONDS публикует наступившие посты.

    Пост считается «наступившим», если текущий день недели и час (по Ташкенту)
    есть в его расписании и он ещё не публиковался в этом часовом слоте.
    Ошибки отдельного поста не роняют цикл.
    """
    store.load()
    logger.info("Планировщик автоповтора запущен (тик каждые %d с)", SCHEDULER_TICK_SECONDS)

    while True:
        try:
            from datetime import datetime
            now_tk = datetime.now(TZ_TASHKENT)
            due = await store.get_due(now_tk)
            for post in due:
                post_id = post["id"]
                try:
                    await publish_post(
                        bot,
                        post["text"],
                        photo_file_id=post.get("photo_file_id"),
                    )
                    await store.mark_run(post_id)
                    logger.info(
                        "Автоповтор поста %s опубликован (%s, %02d:00 Ташкент)",
                        post_id,
                        now_tk.strftime("%a"),
                        now_tk.hour,
                    )
                except (TelegramAPIError, RuntimeError, ValueError) as exc:
                    logger.error("Не удалось переиздать пост %s: %s", post_id, exc)
        except asyncio.CancelledError:
            logger.info("Планировщик автоповтора остановлен")
            raise
        except Exception as exc:  # noqa: BLE001 — цикл не должен падать
            logger.exception("Непредвиденная ошибка в планировщике: %s", exc)

        await asyncio.sleep(SCHEDULER_TICK_SECONDS)
