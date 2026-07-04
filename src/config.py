import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))


def get_bot_token() -> str:
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token":
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in .env")
    return BOT_TOKEN


def get_admin_chat_id() -> int:
    if not ADMIN_CHAT_ID:
        raise RuntimeError("ADMIN_CHAT_ID is not set in .env")
    return ADMIN_CHAT_ID
