from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.language_service import DEFAULT_LANGUAGE, t

REPOST_CALLBACK_PREFIX = "repost:"

_INTERVAL_BUTTONS = (
    (None, "button_repost_off"),
    (6, "button_repost_6h"),
    (12, "button_repost_12h"),
    (24, "button_repost_24h"),
)


def _callback(post_id: str, hours: int | None) -> str:
    value = "off" if hours is None else str(hours)
    return f"{REPOST_CALLBACK_PREFIX}{post_id}:{value}"


def repost_keyboard(
    post_id: str,
    language: str = DEFAULT_LANGUAGE,
    selected_hours: int | None | str = "unset",
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for hours, key in _INTERVAL_BUTTONS:
        text = t(key, language)
        is_selected = (
            hours == selected_hours
            if hours is not None
            else selected_hours is None
        )
        if is_selected:
            text = f"✓ {text}"
        row.append(InlineKeyboardButton(text=text, callback_data=_callback(post_id, hours)))

    buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)
