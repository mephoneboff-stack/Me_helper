from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import SCHEDULE_AVAILABLE_DAYS, SCHEDULE_AVAILABLE_HOURS
from services.language_service import DEFAULT_LANGUAGE, t

REPOST_CALLBACK_PREFIX = "repost:"

# Названия дней недели: 0=Пн … 6=Вс
_DAY_KEYS = {
    0: "day_mon",
    1: "day_tue",
    2: "day_wed",
    3: "day_thu",
    4: "day_fri",
    5: "day_sat",
    6: "day_sun",
}

_HOUR_KEYS = {h: f"hour_{h}" for h in SCHEDULE_AVAILABLE_HOURS}


def _toggle(checked: bool, text: str) -> str:
    return f"✓ {text}" if checked else text


def repost_keyboard(
    post_id: str,
    language: str = DEFAULT_LANGUAGE,
    selected_days: list[int] | None = None,
    selected_hours: list[int] | None = None,
) -> InlineKeyboardMarkup:
    days = set(selected_days or [])
    hours = set(selected_hours or [])

    rows: list[list[InlineKeyboardButton]] = []

    # Ряд 1: дни недели
    day_row = []
    for d in SCHEDULE_AVAILABLE_DAYS:
        key = _DAY_KEYS.get(d)
        if not key:
            continue
        day_row.append(
            InlineKeyboardButton(
                text=_toggle(d in days, t(key, language)),
                callback_data=f"{REPOST_CALLBACK_PREFIX}{post_id}:day:{d}",
            )
        )
    rows.append(day_row)

    # Ряд 2: часы
    hour_row = []
    for h in SCHEDULE_AVAILABLE_HOURS:
        hour_row.append(
            InlineKeyboardButton(
                text=_toggle(h in hours, t(_HOUR_KEYS[h], language)),
                callback_data=f"{REPOST_CALLBACK_PREFIX}{post_id}:hour:{h}",
            )
        )
    rows.append(hour_row)

    # Ряд 3: действия
    rows.append(
        [
            InlineKeyboardButton(
                text=t("button_repost_save", language),
                callback_data=f"{REPOST_CALLBACK_PREFIX}{post_id}:save",
            ),
            InlineKeyboardButton(
                text=t("button_repost_off", language),
                callback_data=f"{REPOST_CALLBACK_PREFIX}{post_id}:off",
            ),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)
