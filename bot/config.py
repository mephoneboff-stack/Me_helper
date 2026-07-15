import os
from datetime import timezone, timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Переменная {name} не задана в .env")

    return value


BOT_TOKEN = _required_env("BOT_TOKEN")
CHANNEL_ID = _required_env("CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

if OPENAI_API_KEY and OPENAI_API_KEY.startswith("gsk_"):
    OPENAI_BASE_URL = OPENAI_BASE_URL or "https://api.groq.com/openai/v1"
    DEFAULT_OPENAI_MODEL = "llama-3.3-70b-versatile"
else:
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

OPENAI_MODEL = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

DATA_DIR = BASE_DIR / "data"
REPOST_DATA_FILE = DATA_DIR / "reposts.json"

SCHEDULER_TICK_SECONDS = int(os.getenv("SCHEDULER_TICK_SECONDS", "60"))

# Часовой пояс Ташкента (UTC+5) — для расписания публикаций
TZ_TASHKENT = timezone(timedelta(hours=5))

# Доступные дни недели (0=Пн … 6=Вс)
SCHEDULE_AVAILABLE_DAYS = (0, 1, 2, 3, 4, 5)

# Доступные часы публикации (по Ташкенту)
SCHEDULE_AVAILABLE_HOURS = (10, 12, 14, 16, 18)

# 11:00 Ташкент (UTC+5) = 06:00 UTC
REPOST_DEFAULT_TIME_UTC = os.getenv("REPOST_DEFAULT_TIME_UTC", "06:00")
