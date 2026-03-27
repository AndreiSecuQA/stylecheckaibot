#!/usr/bin/env python
"""Diagnostic script - run with: ./venv2/bin/python debug_bot.py"""
import sys
import traceback

LOG = "/tmp/stylebot_debug.log"

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(msg + "\n")

with open(LOG, "w") as f:
    f.write("=== debug start ===\n")

log("Step 1: Python OK - version " + sys.version)

try:
    from app.utils.config import settings
    log(f"Step 2: config OK - model={settings.gemini_model}")
except Exception:
    log("FAIL Step 2 config:\n" + traceback.format_exc())
    sys.exit(1)

try:
    from app.utils.logger import logger
    log("Step 3: logger OK")
except Exception:
    log("FAIL Step 3 logger:\n" + traceback.format_exc())
    sys.exit(1)

try:
    from app.db.database import init_db
    log("Step 4: db module OK")
except Exception:
    log("FAIL Step 4 db:\n" + traceback.format_exc())
    sys.exit(1)

try:
    from app.bot.keyboards import main_menu_keyboard, occasion_keyboard
    log("Step 5a: keyboards OK")
except Exception:
    log("FAIL Step 5a keyboards:\n" + traceback.format_exc())
    sys.exit(1)

try:
    from app.bot.handlers import router
    log("Step 5b: handlers OK")
except Exception:
    log("FAIL Step 5b handlers:\n" + traceback.format_exc())
    sys.exit(1)

try:
    from aiogram import Bot, Dispatcher
    log("Step 6: aiogram OK")
except Exception:
    log("FAIL Step 6 aiogram:\n" + traceback.format_exc())
    sys.exit(1)

import asyncio

async def test():
    log("Step 7: running init_db...")
    await init_db()
    log("Step 8: init_db done")

    bot = Bot(token=settings.telegram_bot_token)
    log("Step 9: Bot created OK")

    dp = Dispatcher()
    dp.include_router(router)
    log("Step 10: Dispatcher ready")

    await bot.session.close()
    log("=== ALL CHECKS PASSED - bot should work ===")

asyncio.run(test())

