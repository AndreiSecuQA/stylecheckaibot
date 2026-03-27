
import asyncio
import re
import time
from pathlib import Path
from typing import Optional

import aiofiles
import aiofiles.os

from app.utils.config import settings
from app.utils.logger import logger


def _sanitize_user_id(user_id: int) -> str:
    """Ensure user_id contains only digits to prevent path traversal."""
    sanitized = re.sub(r"[^0-9]", "", str(user_id))
    if not sanitized:
        raise ValueError(f"Invalid user_id for path: {user_id}")
    return sanitized


async def save_image(user_id: int, image_bytes: bytes) -> str:
    """Save image bytes to disk atomically. Returns absolute path string."""
    safe_id = _sanitize_user_id(user_id)
    user_dir = settings.images_dir / safe_id
    user_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time() * 1000)
    filename = f"{timestamp}.jpg"
    target_path = user_dir / filename
    tmp_path = user_dir / f".{filename}.tmp"

    async with aiofiles.open(tmp_path, "wb") as f:
        await f.write(image_bytes)

    # Atomic rename (run in executor to avoid blocking the event loop)
    await asyncio.get_event_loop().run_in_executor(None, tmp_path.rename, target_path)

    abs_path = str(target_path.resolve())
    logger.info("Saved image: %s (%d bytes)", abs_path, len(image_bytes))
    return abs_path


async def delete_image(image_path: str) -> None:
    """Delete an image file. Silently ignores missing files."""
    path = Path(image_path)
    try:
        if path.exists():
            path.unlink()
            logger.info("Deleted image: %s", image_path)
        else:
            logger.debug("Image already missing, skipping: %s", image_path)
    except OSError as e:
        logger.error("Failed to delete image %s: %s", image_path, e)


async def get_latest_image_path(user_id: int) -> Optional[str]:
    """Return the path of the most recently saved image for a user, or None."""
    try:
        safe_id = _sanitize_user_id(user_id)
        user_dir = settings.images_dir / safe_id
        if not user_dir.exists():
            return None
        images = sorted(user_dir.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)
        return str(images[0].resolve()) if images else None
    except Exception as e:
        logger.error("Failed to get latest image for user %s: %s", user_id, e)
        return None


