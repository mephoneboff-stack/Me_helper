from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

PUBLISH_CALLBACK = "post:publish"
EDIT_AGAIN_CALLBACK = "post:edit_again"
CANCEL_CALLBACK = "post:cancel"


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Опубликовать",
                    callback_data=PUBLISH_CALLBACK,
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔁 Улучшить ещё",
                    callback_data=EDIT_AGAIN_CALLBACK,
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data=CANCEL_CALLBACK,
                ),
            ],
        ]
    )
