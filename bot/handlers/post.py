from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.confirm import (
    CANCEL_CALLBACK,
    EDIT_AGAIN_CALLBACK,
    PUBLISH_CALLBACK,
    confirm_keyboard,
)
from keyboards.repost import REPOST_CALLBACK_PREFIX, repost_keyboard
from services.ai_service import edit_text
from services.language_service import get_user_language, t
from services.telegram_service import publish_post
from states.post_state import PostState

router = Router()


@router.message(Command("new"))
async def new_post(message: Message, state: FSMContext):
    language = get_user_language(message.from_user.id if message.from_user else None)
    await state.set_state(PostState.waiting_for_post)
    await message.answer(t("new_prompt", language))


@router.message(Command("cancel"))
async def cancel_post(message: Message, state: FSMContext):
    language = get_user_language(message.from_user.id if message.from_user else None)
    await state.clear()
    await message.answer(t("cancelled", language))


@router.message(Command("test"))
async def test_publish(message: Message):
    language = get_user_language(message.from_user.id if message.from_user else None)
    await publish_post(
        message.bot,
        "🚀 Это тестовая публикация из Me Helper.",
    )
    await message.answer(t("test_published", language))


@router.message(PostState.waiting_for_post)
async def receive_post(message: Message, state: FSMContext):
    language = get_user_language(message.from_user.id if message.from_user else None)
    data = await state.get_data()
    photo_file_id = message.photo[-1].file_id if message.photo else data.get("photo_file_id")
    source_text = (message.caption or message.text or "").strip()

    if message.photo and not source_text:
        await state.update_data(photo_file_id=photo_file_id)
        await message.answer(t("photo_received_need_text", language))
        return

    if not source_text:
        await message.answer(t("missing_text", language))
        return

    status_message = await message.answer(t("editing", language))

    try:
        edited_text = await edit_text(source_text)
    except Exception as exc:
        edited_text = source_text
        await status_message.answer(
            t("ai_failed", language, error=exc)
        )

    await state.update_data(
        photo_file_id=photo_file_id,
        original_text=source_text,
        edited_text=edited_text,
        language=language,
    )
    await state.set_state(PostState.waiting_for_confirmation)

    await status_message.answer(
        _preview_text(edited_text, language),
        reply_markup=confirm_keyboard(language),
    )


@router.callback_query(PostState.waiting_for_confirmation, F.data == EDIT_AGAIN_CALLBACK)
async def edit_again(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get("language") or get_user_language(callback.from_user.id if callback.from_user else None)
    text = data.get("edited_text") or data.get("original_text")

    if not text:
        await callback.answer(t("text_missing", language), show_alert=True)
        await state.clear()
        return

    await callback.answer(t("edit_again_answer", language))

    try:
        edited_text = await edit_text(text)
    except Exception as exc:
        await callback.message.answer(t("edit_again_failed", language, error=exc))
        return

    await state.update_data(edited_text=edited_text)
    await callback.message.edit_text(
        _preview_text(edited_text, language),
        reply_markup=confirm_keyboard(language),
    )


@router.callback_query(PostState.waiting_for_confirmation, F.data == PUBLISH_CALLBACK)
async def publish_confirmed(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get("language") or get_user_language(callback.from_user.id if callback.from_user else None)
    edited_text = data.get("edited_text")

    if not edited_text:
        await callback.answer(t("text_missing", language), show_alert=True)
        await state.clear()
        return

    try:
        await publish_post(
            callback.bot,
            edited_text,
            photo_file_id=data.get("photo_file_id"),
        )
    except Exception as exc:
        await callback.answer(t("publish_failed_alert", language), show_alert=True)
        await callback.message.answer(str(exc))
        return

    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)

    from keyboards.repost import repost_keyboard
    from services.repost_store import add as add_repost

    post = await add_repost(edited_text, data.get("photo_file_id"))
    await callback.message.answer(t("published", language))
    await callback.message.answer(
        t("repost_prompt", language),
        reply_markup=repost_keyboard(post["id"], language),
    )
    await callback.answer()


@router.callback_query(PostState.waiting_for_confirmation, F.data == CANCEL_CALLBACK)
async def cancel_confirmed(callback: CallbackQuery, state: FSMContext):
    language = get_user_language(callback.from_user.id if callback.from_user else None)
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t("publication_cancelled", language))
    await callback.answer()


@router.callback_query(F.data.startswith(REPOST_CALLBACK_PREFIX))
async def set_repost(callback: CallbackQuery):
    if not callback.from_user or not callback.data:
        await callback.answer()
        return

    language = get_user_language(callback.from_user.id)

    payload = callback.data.removeprefix(REPOST_CALLBACK_PREFIX)
    try:
        post_id, value = payload.split(":", 1)
    except ValueError:
        await callback.answer()
        return

    from services.repost_store import get as get_repost, set_interval

    post = await get_repost(post_id)
    if not post:
        await callback.answer(t("repost_missing", language), show_alert=True)
        return

    hours: int | None = None if value == "off" else int(value)
    updated = await set_interval(post_id, hours)
    selected = hours if updated and updated.get("enabled") else None

    message_key = "repost_off" if hours is None else "repost_set"
    alert_kwargs = {} if hours is None else {"hours": hours}
    from services.tg_helpers import safe_edit_text

    await safe_edit_text(
        callback.message,
        t(message_key, language, **alert_kwargs),
        reply_markup=repost_keyboard(post_id, language, selected_hours=selected),
    )
    await callback.answer()


def _preview_text(text: str, language: str) -> str:
    preview = text if len(text) <= 3500 else f"{text[:3500]}..."
    return t("preview", language, text=preview)
