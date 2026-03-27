"""Shared pytest fixtures for StyleCheckAIBot tests."""
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ---------------------------------------------------------------------------
# Make config load without requiring a real .env file in CI / test runs.
# These are set before any app module is imported.
# ---------------------------------------------------------------------------
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test:token")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("LOG_TO_FILE", "0")  # never write log files during tests


# ---------------------------------------------------------------------------
# In-memory async SQLite for database tests
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_session():
    """Provide a fresh in-memory database session for each test."""
    from app.db.models import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Patch the module-level async_session in database.py to use our test engine
    with patch("app.db.database.async_session", session_factory):
        yield session_factory

    await engine.dispose()


# ---------------------------------------------------------------------------
# Temporary directory for image-storage tests
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_images_dir(tmp_path):
    """Return a temporary directory path and patch settings.images_dir."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    with patch("app.storage.image_storage.settings") as mock_settings:
        mock_settings.images_dir = images_dir
        yield images_dir
