from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

LANGUAGE_CALLBACK_PREFIX = "language:"
RU_CALLBACK = f"{LANGUAGE_CALLBACK_PREFIX}ru"
UZ_CALLBACK = f"{LANGUAGE_CALLBACK_PREFIX}uz"


def language_keyboard(selected_language: str | None = None) -> InlineKeyboardMarkup:
    ru_text = "🇷🇺 Рус"
    uz_text = "🇺🇿 Узб"

    if selected_language == "ru":
        ru_text = f"✓ {ru_text}"
    elif selected_language == "uz":
        uz_text = f"✓ {uz_text}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=ru_text, callback_data=RU_CALLBACK),
                InlineKeyboardButton(text=uz_text, callback_data=UZ_CALLBACK),
            ]
        ]
    )
