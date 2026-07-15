import asyncio
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone

from config import REPOST_DATA_FILE

logger = logging.getLogger(__name__)

_lock = asyncio.Lock()
_posts: list[dict] = []
_loaded = False

INTERVAL_CHOICES = (6, 12, 24)


def _now() -> datetime:
    return datetime.now(timezone.utc)


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
            _posts.extend(p for p in data if isinstance(p, dict))
        logger.info("Загружено постов для автоповтора: %d", len(_posts))
    except FileNotFoundError:
        pass
    except Exception as exc:
        logger.warning("Не удалось прочитать %s: %s", REPOST_DATA_FILE, exc)


async def _save() -> None:
    REPOST_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPOST_DATA_FILE.write_text(
        json.dumps(_posts, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


async def add(
    text: str,
    photo_file_id: str | None,
    interval_hours: int | None = None,
    enabled: bool = False,
) -> dict:
    """Создаёт запись. Без interval_hours — «висящий» пост, ждёт выбора интервала."""
    async with _lock:
        now = _now()
        post = {
            "id": _new_id(),
            "text": text,
            "photo_file_id": photo_file_id,
            "interval_hours": interval_hours,
            "next_run_at": _iso(now + timedelta(hours=interval_hours)) if interval_hours else _iso(now),
            "enabled": enabled,
            "created_at": _iso(now),
        }
        _posts.append(post)
        await _save()
        return post


async def set_interval(post_id: str, interval_hours: int | None) -> dict | None:
    """interval_hours=None → выключить повтор; иначе задать новый интервал."""
    async with _lock:
        for post in _posts:
            if post["id"] != post_id:
                continue
            if interval_hours is None:
                post["enabled"] = False
            else:
                post["interval_hours"] = interval_hours
                post["enabled"] = True
                post["next_run_at"] = _iso(_now() + timedelta(hours=interval_hours))
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


async def get_due(now: datetime | None = None) -> list[dict]:
    moment = now or _now()
    async with _lock:
        return [
            dict(post)
            for post in _posts
            if post.get("enabled") and _parse_dt(post["next_run_at"]) <= moment
        ]


async def schedule_next(post_id: str) -> None:
    async with _lock:
        for post in _posts:
            if post["id"] == post_id:
                post["next_run_at"] = _iso(_now() + timedelta(hours=post["interval_hours"]))
                await _save()
                return
