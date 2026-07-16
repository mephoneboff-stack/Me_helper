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


def _extract_media(message: Message) -> tuple[str | None, str | None]:
    """Извлекает (media_type, file_id) из сообщения. Приоритет: photo > video > animation > document."""
    if message.photo:
        return "photo", message.photo[-1].file_id
    if message.video:
        return "video", message.video.file_id
    if message.animation:
        return "animation", message.animation.file_id
    if message.document:
        return "document", message.document.file_id
    return None, None


@router.message(PostState.waiting_for_post)
async def receive_post(message: Message, state: FSMContext):
    language = get_user_language(message.from_user.id if message.from_user else None)
    data = await state.get_data()
    media_type, file_id = _extract_media(message)
    # Если пришёл только текст, но ранее было вложение — берём из стейта
    if not media_type:
        media_type = data.get("media_type")
        file_id = data.get("file_id")
    source_text = (message.caption or message.text or "").strip()

    if media_type and not source_text:
        await state.update_data(media_type=media_type, file_id=file_id)
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
        media_type=media_type,
        file_id=file_id,
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
            media_type=data.get("media_type"),
            file_id=data.get("file_id"),
        )
    except Exception as exc:
        await callback.answer(t("publish_failed_alert", language), show_alert=True)
        await callback.message.answer(str(exc))
        return

    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)

    from keyboards.repost import repost_keyboard
    from services.repost_store import add as add_repost

    post = await add_repost(edited_text, data.get("file_id"), media_type=data.get("media_type"))
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
    # Формат: {post_id}:day:{0-6} | {post_id}:hour:{H} | {post_id}:save | {post_id}:off
    try:
        post_id, action, *rest = payload.split(":")
    except ValueError:
        await callback.answer()
        return

    from keyboards.repost import repost_keyboard
    from services.repost_store import (
        disable as disable_repost,
        get as get_repost,
        set_schedule,
    )
    from services.tg_helpers import safe_edit_text

    post = await get_repost(post_id)
    if not post:
        await callback.answer(t("repost_missing", language), show_alert=True)
        return

    # Текущий выбор из записи (независимо от того, сохранён ли он уже)
    days = set(post.get("schedule_days") or [])
    hours = set(post.get("schedule_hours") or [])

    if action == "day":
        day = int(rest[0])
        days = days ^ {day}  # toggle
        await set_schedule(post_id, list(days), list(hours))
        await safe_edit_text(
            callback.message,
            t("repost_prompt", language),
            reply_markup=repost_keyboard(post_id, language, list(days), list(hours)),
        )
    elif action == "hour":
        hour = int(rest[0])
        hours = hours ^ {hour}  # toggle
        await set_schedule(post_id, list(days), list(hours))
        await safe_edit_text(
            callback.message,
            t("repost_prompt", language),
            reply_markup=repost_keyboard(post_id, language, list(days), list(hours)),
        )
    elif action == "save":
        if not days or not hours:
            await callback.answer(t("repost_need_day_hour", language), show_alert=True)
            return
        await safe_edit_text(
            callback.message,
            t(
                "repost_saved",
                language,
                days=_format_days(days, language),
                hours=_format_hours(hours, language),
            ),
            reply_markup=repost_keyboard(post_id, language, list(days), list(hours)),
        )
    elif action == "off":
        await disable_repost(post_id)
        await safe_edit_text(
            callback.message,
            t("repost_off", language),
            reply_markup=repost_keyboard(post_id, language, [], []),
        )
    else:
        await callback.answer()
        return

    await callback.answer()


def _format_days(days: set[int], language: str) -> str:
    _day_keys = {
        0: "day_mon", 1: "day_tue", 2: "day_wed",
        3: "day_thu", 4: "day_fri", 5: "day_sat", 6: "day_sun",
    }
    return ", ".join(t(_day_keys[d], language) for d in sorted(days) if d in _day_keys)


def _format_hours(hours: set[int], language: str) -> str:
    return ", ".join(f"{h:02d}:00" for h in sorted(hours))


def _preview_text(text: str, language: str) -> str:
    preview = text if len(text) <= 3500 else f"{text[:3500]}..."
    return t("preview", language, text=preview)
