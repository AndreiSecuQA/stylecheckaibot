import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, OutfitCheck, User
from app.utils.config import settings
from app.utils.logger import logger

_db_dir = Path(settings.db_path).parent
_db_dir.mkdir(parents=True, exist_ok=True)

_db_url = f"sqlite+aiosqlite:///{settings.db_path}"

engine = create_async_engine(_db_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.run_sync(Base.metadata.create_all)
        migrations = [
            "ALTER TABLE users ADD COLUMN language VARCHAR DEFAULT 'en' NOT NULL",
            "ALTER TABLE users ADD COLUMN name VARCHAR DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN height_cm INTEGER DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN weight_kg INTEGER DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN onboarding_complete BOOLEAN DEFAULT 0 NOT NULL",
            "ALTER TABLE users ADD COLUMN last_flow_image_path VARCHAR DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN gemini_api_key VARCHAR DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT 0 NOT NULL",
            "ALTER TABLE users ADD COLUMN free_uses_remaining INTEGER DEFAULT 5 NOT NULL",
            # Fix: existing users who got free_uses_remaining=0 from old schema get reset to 5
            "UPDATE users SET free_uses_remaining = 5 WHERE free_uses_remaining = 0 AND gemini_api_key IS NULL AND is_approved = 0",
        ]
        for sql in migrations:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass
    logger.info("Database initialized (WAL mode enabled)")


async def get_or_create_user(telegram_user_id: int) -> User:
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_user_id=telegram_user_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info("Created new user: tg_id=%s", telegram_user_id)
        return user


async def upsert_occasion(telegram_user_id: int, occasion: str) -> None:
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_user_id=telegram_user_id, selected_occasion=occasion)
            session.add(user)
        else:
            user.selected_occasion = occasion
        await session.commit()
        logger.info("Occasion set to '%s' for tg_id=%s", occasion, telegram_user_id)


async def upsert_language(telegram_user_id: int, language: str) -> None:
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_user_id=telegram_user_id, language=language)
            session.add(user)
        else:
            user.language = language
        await session.commit()
        logger.info("Language set to '%s' for tg_id=%s", language, telegram_user_id)


async def get_user_language(telegram_user_id: int) -> str:
    async with async_session() as session:
        stmt = select(User.language).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        lang = result.scalar_one_or_none()
        return lang if lang else "en"


async def get_user_occasion(telegram_user_id: int) -> Optional[str]:
    async with async_session() as session:
        stmt = select(User.selected_occasion).where(
            User.telegram_user_id == telegram_user_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def check_daily_limit(telegram_user_id: int) -> bool:
    today = datetime.date.today()
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                telegram_user_id=telegram_user_id,
                daily_check_count=1,
                last_check_date=today,
            )
            session.add(user)
            await session.commit()
            return True
        if user.last_check_date != today:
            user.daily_check_count = 0
            user.last_check_date = today
        if user.daily_check_count >= settings.max_checks_per_day:
            return False
        user.daily_check_count += 1
        user.last_check_date = today
        await session.commit()
        return True


async def save_outfit_check(
    telegram_user_id: int, image_path: str, result_text: str
) -> None:
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_user_id=telegram_user_id)
            session.add(user)
            await session.flush()
        check = OutfitCheck(
            user_id=user.id,
            image_path=image_path,
            result_text=result_text,
        )
        session.add(check)
        await session.flush()
        all_checks_stmt = (
            select(OutfitCheck)
            .where(OutfitCheck.user_id == user.id)
            .order_by(OutfitCheck.created_at.desc())
        )
        all_result = await session.execute(all_checks_stmt)
        all_checks = list(all_result.scalars().all())
        old_image_paths: List[str] = []
        if len(all_checks) > settings.max_stored_checks:
            to_delete = all_checks[settings.max_stored_checks:]
            old_image_paths = [c.image_path for c in to_delete]
            ids_to_delete = [c.id for c in to_delete]
            await session.execute(
                delete(OutfitCheck).where(OutfitCheck.id.in_(ids_to_delete))
            )
        await session.commit()
        logger.info(
            "Saved outfit check for tg_id=%s, pruned %d old checks",
            telegram_user_id,
            len(old_image_paths),
        )
        from app.storage.image_storage import delete_image
        for path in old_image_paths:
            await delete_image(path)


async def complete_onboarding(
    telegram_user_id: int, name: str, height_cm: int, weight_kg: int
) -> None:
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_user_id=telegram_user_id)
            session.add(user)
        user.name = name
        user.height_cm = height_cm
        user.weight_kg = weight_kg
        user.onboarding_complete = True
        await session.commit()
        logger.info("Onboarding complete for tg_id=%s", telegram_user_id)


async def is_onboarding_complete(telegram_user_id: int) -> bool:
    async with async_session() as session:
        stmt = select(User.onboarding_complete).where(
            User.telegram_user_id == telegram_user_id
        )
        result = await session.execute(stmt)
        val = result.scalar_one_or_none()
        return bool(val)


async def get_user_body_params(telegram_user_id: int) -> Dict:
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return {"name": None, "height_cm": None, "weight_kg": None, "language": "en"}
        return {
            "name": user.name,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "language": user.language,
        }


async def set_last_flow_image(telegram_user_id: int, image_path: str) -> None:
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_user_id=telegram_user_id, last_flow_image_path=image_path)
            session.add(user)
        else:
            user.last_flow_image_path = image_path
        await session.commit()


async def get_last_flow_image(telegram_user_id: int) -> Optional[str]:
    async with async_session() as session:
        stmt = select(User.last_flow_image_path).where(
            User.telegram_user_id == telegram_user_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


# ── Access control ─────────────────────────────────────────────────────────────

async def get_user_access(telegram_user_id: int) -> Tuple[bool, Optional[str], int]:
    """
    Returns (has_access, gemini_api_key_or_None, free_uses_remaining).
    Logic:
      - own key  → unlimited access, use their key
      - approved → unlimited access, use system key (key=None)
      - free uses remaining > 0 → limited access, use system key
      - else → no access
    """
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return False, None, 0
        if user.gemini_api_key:
            return True, user.gemini_api_key, -1  # -1 = unlimited via own key
        if user.is_approved:
            return True, None, -1  # -1 = unlimited via admin approval
        if user.free_uses_remaining > 0:
            return True, None, user.free_uses_remaining
        return False, None, 0


async def decrement_free_uses(telegram_user_id: int) -> int:
    """Decrement free uses counter. Returns remaining count after decrement."""
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return 0
        if user.free_uses_remaining > 0:
            user.free_uses_remaining = max(0, user.free_uses_remaining - 1)
            await session.commit()
            return user.free_uses_remaining
        return 0


async def set_gemini_api_key(telegram_user_id: int, api_key: str) -> None:
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_user_id=telegram_user_id, gemini_api_key=api_key)
            session.add(user)
        else:
            user.gemini_api_key = api_key
        await session.commit()
        logger.info("Gemini API key saved for tg_id=%s", telegram_user_id)


async def approve_user(telegram_user_id: int) -> bool:
    """Approve user for unlimited access. Returns True if user was found."""
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return False
        user.is_approved = True
        await session.commit()
        logger.info("User tg_id=%s approved by admin", telegram_user_id)
        return True


async def get_all_users_summary() -> List[Dict]:
    """Return list of users for admin overview."""
    async with async_session() as session:
        stmt = select(User).order_by(User.created_at.desc())
        result = await session.execute(stmt)
        users = result.scalars().all()
        return [
            {
                "telegram_user_id": u.telegram_user_id,
                "name": u.name or "—",
                "language": u.language,
                "is_approved": u.is_approved,
                "has_own_key": bool(u.gemini_api_key),
                "free_uses_remaining": u.free_uses_remaining,
                "onboarding_complete": u.onboarding_complete,
                "created_at": u.created_at,
            }
            for u in users
        ]
