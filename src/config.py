import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
PORT = int(os.getenv("PORT", "8000"))
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
DB_PATH = os.getenv("DB_PATH", "data/quiz.db")

_raw_webhook = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL", "")
if _raw_webhook:
    _raw_webhook = _raw_webhook.rstrip("/")
    if not _raw_webhook.endswith(WEBHOOK_PATH):
        _raw_webhook = _raw_webhook + WEBHOOK_PATH
WEBHOOK_URL = _raw_webhook


def get_bot_token() -> str:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    return TELEGRAM_BOT_TOKEN


def get_admin_chat_id() -> int:
    if not ADMIN_CHAT_ID:
        raise RuntimeError("ADMIN_CHAT_ID is not set")
    return ADMIN_CHAT_ID
