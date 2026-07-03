import os
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
