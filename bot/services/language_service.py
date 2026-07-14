DEFAULT_LANGUAGE = "ru"
SUPPORTED_LANGUAGES = {"ru", "uz"}

_user_languages: dict[int, str] = {}

MESSAGES = {
    "start": {
        "ru": (
            "👋 Добро пожаловать в Me Helper!\n\n"
            "Отправьте /new, затем пришлите фото товара с подписью или просто текст.\n"
            "Я улучшу текст, покажу результат и опубликую его только после подтверждения.\n\n"
            "Язык можно изменить через /language."
        ),
        "uz": (
            "👋 Me Helper'ga xush kelibsiz!\n\n"
            "/new buyrug'ini yuboring, keyin mahsulot rasmini izoh bilan yoki faqat matn yuboring.\n"
            "Men matnni yaxshilab, natijani ko'rsataman va faqat tasdiqlaganingizdan keyin kanalga joylayman.\n\n"
            "Tilni /language orqali o'zgartirish mumkin."
        ),
    },
    "language_prompt": {
        "ru": "Выберите язык:",
        "uz": "Tilni tanlang:",
    },
    "language_ru_selected": {
        "ru": "Язык выбран: Русский.",
        "uz": "Til tanlandi: Rus tili.",
    },
    "language_uz_selected": {
        "ru": "Язык выбран: Узбекский.",
        "uz": "Til tanlandi: O'zbek tili.",
    },
    "new_prompt": {
        "ru": (
            "📷 Отправьте фото товара с подписью или просто текст для публикации.\n\n"
            "После этого я улучшу текст с помощью AI и покажу предпросмотр."
        ),
        "uz": (
            "📷 Mahsulot rasmini izoh bilan yoki faqat e'lon matnini yuboring.\n\n"
            "Shundan keyin AI yordamida matnni yaxshilab, ko'rib chiqish uchun ko'rsataman."
        ),
    },
    "cancelled": {
        "ru": "Ок, публикация отменена.",
        "uz": "Xo'p, e'lon bekor qilindi.",
    },
    "test_published": {
        "ru": "✅ Сообщение отправлено в канал.",
        "uz": "✅ Xabar kanalga yuborildi.",
    },
    "photo_received_need_text": {
        "ru": "Фото получено. Теперь отправьте текст для публикации.",
        "uz": "Rasm qabul qilindi. Endi e'lon matnini yuboring.",
    },
    "missing_text": {
        "ru": "Добавьте текст к фото или отправьте текст отдельным сообщением.",
        "uz": "Rasmga matn qo'shing yoki matnni alohida xabar qilib yuboring.",
    },
    "editing": {
        "ru": "Редактирую текст с помощью AI...",
        "uz": "Matn AI yordamida tahrirlanmoqda...",
    },
    "ai_failed": {
        "ru": "AI-редактирование сейчас недоступно: {error}\n\nПоказываю исходный текст для подтверждения.",
        "uz": "AI-tahrirlash hozir ishlamayapti: {error}\n\nTasdiqlash uchun asl matnni ko'rsataman.",
    },
    "preview": {
        "ru": "Предпросмотр публикации:\n\n{text}",
        "uz": "E'lon ko'rinishi:\n\n{text}",
    },
    "text_missing": {
        "ru": "Текст не найден. Начните заново через /new.",
        "uz": "Matn topilmadi. /new orqali qaytadan boshlang.",
    },
    "edit_again_answer": {
        "ru": "Ещё раз улучшаю текст...",
        "uz": "Matn yana yaxshilanmoqda...",
    },
    "edit_again_failed": {
        "ru": "Не удалось повторно улучшить текст: {error}",
        "uz": "Matnni qayta yaxshilab bo'lmadi: {error}",
    },
    "publish_failed_alert": {
        "ru": "Не удалось опубликовать пост.",
        "uz": "E'lonni joylab bo'lmadi.",
    },
    "published": {
        "ru": "✅ Пост опубликован в канал.",
        "uz": "✅ E'lon kanalga joylandi.",
    },
    "publication_cancelled": {
        "ru": "Публикация отменена.",
        "uz": "E'lon bekor qilindi.",
    },
    "button_publish": {
        "ru": "✅ Опубликовать",
        "uz": "✅ Joylash",
    },
    "button_edit_again": {
        "ru": "🔁 Улучшить ещё",
        "uz": "🔁 Yana yaxshilash",
    },
    "button_cancel": {
        "ru": "❌ Отмена",
        "uz": "❌ Bekor qilish",
    },
}


def get_user_language(user_id: int | None) -> str:
    if user_id is None:
        return DEFAULT_LANGUAGE

    return _user_languages.get(user_id, DEFAULT_LANGUAGE)


def set_user_language(user_id: int, language: str) -> str:
    normalized_language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    _user_languages[user_id] = normalized_language
    return normalized_language


def t(key: str, language: str, **kwargs) -> str:
    translations = MESSAGES[key]
    template = translations.get(language, translations[DEFAULT_LANGUAGE])
    return template.format(**kwargs)
