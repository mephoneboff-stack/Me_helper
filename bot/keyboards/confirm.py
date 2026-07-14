from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.language_service import DEFAULT_LANGUAGE, t

PUBLISH_CALLBACK = "post:publish"
EDIT_AGAIN_CALLBACK = "post:edit_again"
CANCEL_CALLBACK = "post:cancel"


def confirm_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("button_publish", language),
                    callback_data=PUBLISH_CALLBACK,
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("button_edit_again", language),
                    callback_data=EDIT_AGAIN_CALLBACK,
                ),
                InlineKeyboardButton(
                    text=t("button_cancel", language),
                    callback_data=CANCEL_CALLBACK,
                ),
            ],
        ]
    )
