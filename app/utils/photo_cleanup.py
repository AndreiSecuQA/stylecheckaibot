"""Auto-delete user photos after a set delay and notify the user."""
from __future__ import annotations

import asyncio

from aiogram import Bot

from app.storage.image_storage import delete_image
from app.utils.i18n import t
from app.utils.logger import logger

_DELETION_DELAY_SECONDS = 15 * 60  # 15 minutes


async def schedule_photo_deletion(
    bot: Bot,
    user_id: int,
    image_path: str,
    lang: str,
    delay: int = _DELETION_DELAY_SECONDS,
) -> None:
    """Wait `delay` seconds, delete the image, then notify the user."""
    await asyncio.sleep(delay)
    await delete_image(image_path)
    try:
        await bot.send_message(user_id, t("photo_deleted", lang))
    except Exception as exc:
        logger.warning(
            "Could not send photo-deleted notification to user %s: %s", user_id, exc
        )
