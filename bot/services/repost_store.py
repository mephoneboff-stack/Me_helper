import asyncio
import json
import logging
import secrets
from datetime import datetime, timezone, timedelta

from config import REPOST_DATA_FILE, TZ_TASHKENT

logger = logging.getLogger(__name__)

_lock = asyncio.Lock()
_posts: list[dict] = []
_loaded = False


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _now_tashkent() -> datetime:
    return datetime.now(TZ_TASHKENT)


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _new_id() -> str:
    return secrets.token_hex(4)


def load() -> None:
    """Загружает хранилище из файла. Падает мягко — пустой список при отсутствии."""
    global _loaded
    if _loaded:
        return
    _loaded = True
    try:
        raw = REPOST_DATA_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            for p in data:
                if not isinstance(p, dict):
                    continue
                _migrate(p)
                _posts.append(p)
        logger.info("Загружено постов для автоповтора: %d", len(_posts))
    except FileNotFoundError:
        pass
    except Exception as exc:
        logger.warning("Не удалось прочитать %s: %s", REPOST_DATA_FILE, exc)


def _migrate(post: dict) -> None:
    """Обратная совместимость со старыми записями (interval_hours → schedule)."""
    if "schedule_days" not in post:
        if post.get("interval_hours"):
            post["schedule_days"] = [0, 1, 2, 3, 4, 5]
            post["schedule_hours"] = list(range(0, 24, post["interval_hours"]))
        else:
            post["schedule_days"] = []
            post["schedule_hours"] = []
        post.pop("interval_hours", None)
        post.pop("next_run_at", None)
    post.setdefault("last_run_at", None)


async def _save() -> None:
    REPOST_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPOST_DATA_FILE.write_text(
        json.dumps(_posts, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


async def add(text: str, photo_file_id: str | None) -> dict:
    """Создаёт запись без расписания — ждёт выбора дней/часов."""
    async with _lock:
        now = _now_utc()
        post = {
            "id": _new_id(),
            "text": text,
            "photo_file_id": photo_file_id,
            "schedule_days": [],
            "schedule_hours": [],
            "last_run_at": None,
            "created_at": _iso(now),
        }
        _posts.append(post)
        await _save()
        return post


async def set_schedule(
    post_id: str, days: list[int], hours: list[int]
) -> dict | None:
    """Сохраняет выбранное расписание. Пустые days/hours → выключено."""
    async with _lock:
        for post in _posts:
            if post["id"] != post_id:
                continue
            post["schedule_days"] = sorted(set(days))
            post["schedule_hours"] = sorted(set(hours))
            await _save()
            return post
    return None


async def disable(post_id: str) -> dict | None:
    """Выключает повтор, очищая расписание."""
    async with _lock:
        for post in _posts:
            if post["id"] != post_id:
                continue
            post["schedule_days"] = []
            post["schedule_hours"] = []
            await _save()
            return post
    return None


async def remove(post_id: str) -> bool:
    async with _lock:
        for i, post in enumerate(_posts):
            if post["id"] == post_id:
                _posts.pop(i)
                await _save()
                return True
    return False


async def get(post_id: str) -> dict | None:
    async with _lock:
        for post in _posts:
            if post["id"] == post_id:
                return dict(post)
    return None


def _is_due(post: dict, now_tk: datetime) -> bool:
    days = post.get("schedule_days") or []
    hours = post.get("schedule_hours") or []
    if not days or not hours:
        return False
    if now_tk.weekday() not in days:
        return False
    if now_tk.hour not in hours:
        return False
    # Защита от дублирования в течение одного часа
    last = post.get("last_run_at")
    if last:
        last_dt = _parse_dt(last).astimezone(TZ_TASHKENT)
        if last_dt.date() == now_tk.date() and last_dt.hour == now_tk.hour:
            return False
    return True


async def get_due(now_tk: datetime | None = None) -> list[dict]:
    moment = now_tk or _now_tashkent()
    async with _lock:
        return [dict(p) for p in _posts if _is_due(p, moment)]


async def mark_run(post_id: str) -> None:
    """Отмечает, что пост опубликован в текущий час (защита от дублей)."""
    async with _lock:
        for post in _posts:
            if post["id"] == post_id:
                post["last_run_at"] = _iso(_now_utc())
                await _save()
                return
