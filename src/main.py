import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from src.config import get_bot_token, WEBHOOK_URL, WEBHOOK_PATH, PORT
from src.bot import router
from src.db import init_db

logger = logging.getLogger(__name__)


async def on_startup(app: web.Application):
    await init_db()
    await app["bot"].set_webhook(WEBHOOK_URL)
    logger.info("Webhook set: %s", WEBHOOK_URL)


async def health_handler(request: web.Request):
    return web.json_response({"status": "ok"})


def main() -> None:
    bot = Bot(token=get_bot_token())
    dp = Dispatcher()
    dp.include_router(router)

    app = web.Application()
    app["bot"] = bot
    app.router.add_get("/health", health_handler)
    SimpleRequestHandler(dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
