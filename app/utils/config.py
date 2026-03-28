import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

# Module-level base dir so dataclass defaults can reference it
_BASE_DIR = Path(__file__).resolve().parent.parent


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Set it in your .env file or export it."
        )
    return value


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    gemini_api_key: str

    # Paths — overridable via env vars for containerised deployments (e.g. Railway volumes)
    base_dir: Path = _BASE_DIR
    db_path: Path = Path(os.getenv("DB_PATH", str(_BASE_DIR / "db" / "stylecheck.db")))
    images_dir: Path = Path(os.getenv("IMAGES_DIR", str(_BASE_DIR / "storage" / "images")))

    # Limits
    max_image_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    max_checks_per_day: int = 15
    max_stored_checks: int = 3

    # Gemini
    gemini_model: str = "gemini-2.0-flash-lite"

    # Admin — Telegram user ID of the bot administrator
    # Set ADMIN_TELEGRAM_ID in your .env file or Railway environment variables
    admin_telegram_id: int = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))


settings = Settings(
    telegram_bot_token=_require_env("TELEGRAM_BOT_TOKEN"),
    gemini_api_key=_require_env("GEMINI_API_KEY"),
)
