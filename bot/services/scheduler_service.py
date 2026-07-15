import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

import services.repost_store as store
from config import SCHEDULER_TICK_SECONDS
from services.telegram_service import publish_post

logger = logging.getLogger(__name__)


async def run_scheduler(bot: Bot) -> None:
    """Фоновый цикл: раз в SCHEDULER_TICK_SECONDS публикует наступившие посты.

    Ошибки отдельного поста не роняют цикл — пост просто переносится дальше.
    """
    store.load()
    logger.info("Планировщик автоповтора запущен (тик каждые %d с)", SCHEDULER_TICK_SECONDS)

    while True:
        try:
            due = await store.get_due()
            for post in due:
                post_id = post["id"]
                try:
                    await publish_post(
                        bot,
                        post["text"],
                        photo_file_id=post.get("photo_file_id"),
                    )
                    logger.info("Автоповтор поста %s опубликован", post_id)
                except (TelegramAPIError, RuntimeError, ValueError) as exc:
                    logger.error("Не удалось переиздать пост %s: %s", post_id, exc)
                finally:
                    await store.schedule_next(post_id)
        except asyncio.CancelledError:
            logger.info("Планировщик автоповтора остановлен")
            raise
        except Exception as exc:  # noqa: BLE001 — цикл не должен падать
            logger.exception("Непредвиденная ошибка в планировщике: %s", exc)

        await asyncio.sleep(SCHEDULER_TICK_SECONDS)
