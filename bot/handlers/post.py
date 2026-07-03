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
from services.ai_service import edit_text
from services.telegram_service import publish_post
from states.post_state import PostState

router = Router()


@router.message(Command("new"))
async def new_post(message: Message, state: FSMContext):
    await state.set_state(PostState.waiting_for_post)
    await message.answer(
        "📷 Отправьте фото товара с подписью или просто текст для публикации.\n\n"
        "После этого я улучшу текст с помощью AI и покажу предпросмотр."
    )


@router.message(Command("cancel"))
async def cancel_post(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Ок, публикация отменена.")


@router.message(Command("test"))
async def test_publish(message: Message):
    await publish_post(
        message.bot,
        "🚀 Это тестовая публикация из Me Helper.",
    )
    await message.answer("✅ Сообщение отправлено в канал.")


@router.message(PostState.waiting_for_post)
async def receive_post(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_file_id = message.photo[-1].file_id if message.photo else data.get("photo_file_id")
    source_text = (message.caption or message.text or "").strip()

    if message.photo and not source_text:
        await state.update_data(photo_file_id=photo_file_id)
        await message.answer("Фото получено. Теперь отправьте текст для публикации.")
        return

    if not source_text:
        await message.answer("Добавьте текст к фото или отправьте текст отдельным сообщением.")
        return

    status_message = await message.answer("Редактирую текст с помощью AI...")

    try:
        edited_text = await edit_text(source_text)
    except Exception as exc:
        edited_text = source_text
        await status_message.answer(
            f"AI-редактирование сейчас недоступно: {exc}\n\n"
            "Показываю исходный текст для подтверждения."
        )

    await state.update_data(
        photo_file_id=photo_file_id,
        original_text=source_text,
        edited_text=edited_text,
    )
    await state.set_state(PostState.waiting_for_confirmation)

    await status_message.answer(
        _preview_text(edited_text),
        reply_markup=confirm_keyboard(),
    )


@router.callback_query(PostState.waiting_for_confirmation, F.data == EDIT_AGAIN_CALLBACK)
async def edit_again(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("edited_text") or data.get("original_text")

    if not text:
        await callback.answer("Текст не найден. Начните заново через /new.", show_alert=True)
        await state.clear()
        return

    await callback.answer("Ещё раз улучшаю текст...")

    try:
        edited_text = await edit_text(text)
    except Exception as exc:
        await callback.message.answer(f"Не удалось повторно улучшить текст: {exc}")
        return

    await state.update_data(edited_text=edited_text)
    await callback.message.edit_text(
        _preview_text(edited_text),
        reply_markup=confirm_keyboard(),
    )


@router.callback_query(PostState.waiting_for_confirmation, F.data == PUBLISH_CALLBACK)
async def publish_confirmed(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    edited_text = data.get("edited_text")

    if not edited_text:
        await callback.answer("Текст не найден. Начните заново через /new.", show_alert=True)
        await state.clear()
        return

    try:
        await publish_post(
            callback.bot,
            edited_text,
            photo_file_id=data.get("photo_file_id"),
        )
    except Exception as exc:
        await callback.answer("Не удалось опубликовать пост.", show_alert=True)
        await callback.message.answer(str(exc))
        return

    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ Пост опубликован в канал.")
    await callback.answer()


@router.callback_query(PostState.waiting_for_confirmation, F.data == CANCEL_CALLBACK)
async def cancel_confirmed(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Публикация отменена.")
    await callback.answer()


def _preview_text(text: str) -> str:
    preview = text if len(text) <= 3500 else f"{text[:3500]}..."
    return f"Предпросмотр публикации:\n\n{preview}"
