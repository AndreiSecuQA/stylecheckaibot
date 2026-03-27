"""Unit tests for app/db/database.py using an in-memory SQLite database."""
import datetime
from unittest.mock import patch

import pytest


class TestGetOrCreateUser:
    async def test_creates_new_user(self, db_session):
        from app.db.database import get_or_create_user
        user = await get_or_create_user(111)
        assert user.telegram_user_id == 111
        assert user.id is not None

    async def test_returns_existing_user(self, db_session):
        from app.db.database import get_or_create_user
        u1 = await get_or_create_user(222)
        u2 = await get_or_create_user(222)
        assert u1.id == u2.id

    async def test_different_users_have_different_ids(self, db_session):
        from app.db.database import get_or_create_user
        u1 = await get_or_create_user(301)
        u2 = await get_or_create_user(302)
        assert u1.id != u2.id


class TestUpsertLanguage:
    async def test_sets_language(self, db_session):
        from app.db.database import get_or_create_user, get_user_language, upsert_language
        await get_or_create_user(400)
        await upsert_language(400, "ro")
        lang = await get_user_language(400)
        assert lang == "ro"

    async def test_updates_existing_language(self, db_session):
        from app.db.database import get_or_create_user, get_user_language, upsert_language
        await get_or_create_user(401)
        await upsert_language(401, "en")
        await upsert_language(401, "ro")
        assert await get_user_language(401) == "ro"

    async def test_default_language_is_en(self, db_session):
        from app.db.database import get_or_create_user, get_user_language
        await get_or_create_user(402)
        lang = await get_user_language(402)
        assert lang == "en"

    async def test_unknown_user_language_returns_en(self, db_session):
        from app.db.database import get_user_language
        lang = await get_user_language(999999)
        assert lang == "en"


class TestUpsertOccasion:
    async def test_sets_occasion(self, db_session):
        from app.db.database import get_or_create_user, get_user_occasion, upsert_occasion
        await get_or_create_user(500)
        await upsert_occasion(500, "Casual")
        occ = await get_user_occasion(500)
        assert occ == "Casual"

    async def test_updates_occasion(self, db_session):
        from app.db.database import get_or_create_user, get_user_occasion, upsert_occasion
        await get_or_create_user(501)
        await upsert_occasion(501, "Work")
        await upsert_occasion(501, "Party")
        assert await get_user_occasion(501) == "Party"

    async def test_no_occasion_returns_none(self, db_session):
        from app.db.database import get_or_create_user, get_user_occasion
        await get_or_create_user(502)
        assert await get_user_occasion(502) is None


class TestCheckDailyLimit:
    async def test_first_check_allowed(self, db_session):
        from app.db.database import check_daily_limit, get_or_create_user
        await get_or_create_user(600)
        assert await check_daily_limit(600) is True

    async def test_limit_not_exceeded_within_max(self, db_session):
        from app.db.database import check_daily_limit, get_or_create_user
        from app.utils.config import settings
        await get_or_create_user(601)
        for _ in range(settings.max_checks_per_day - 1):
            assert await check_daily_limit(601) is True

    async def test_limit_exceeded_returns_false(self, db_session):
        from app.db.database import check_daily_limit, get_or_create_user
        from app.utils.config import settings
        await get_or_create_user(602)
        for _ in range(settings.max_checks_per_day):
            await check_daily_limit(602)
        assert await check_daily_limit(602) is False

    async def test_count_resets_on_new_day(self, db_session):
        from app.db.database import check_daily_limit, get_or_create_user
        from app.utils.config import settings
        await get_or_create_user(603)
        # Exhaust limit
        for _ in range(settings.max_checks_per_day):
            await check_daily_limit(603)
        # Simulate tomorrow
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        with patch("app.db.database.datetime") as mock_dt:
            mock_dt.date.today.return_value = tomorrow
            assert await check_daily_limit(603) is True


class TestCompleteOnboarding:
    async def test_complete_onboarding_sets_all_fields(self, db_session):
        from app.db.database import complete_onboarding, get_or_create_user, get_user_body_params, is_onboarding_complete
        await get_or_create_user(700)
        await complete_onboarding(700, "Alice", 165, 60)
        assert await is_onboarding_complete(700) is True
        params = await get_user_body_params(700)
        assert params["name"] == "Alice"
        assert params["height_cm"] == 165
        assert params["weight_kg"] == 60

    async def test_is_onboarding_complete_false_by_default(self, db_session):
        from app.db.database import get_or_create_user, is_onboarding_complete
        await get_or_create_user(701)
        assert await is_onboarding_complete(701) is False

    async def test_unknown_user_onboarding_returns_false(self, db_session):
        from app.db.database import is_onboarding_complete
        assert await is_onboarding_complete(999998) is False

    async def test_get_body_params_unknown_user_returns_defaults(self, db_session):
        from app.db.database import get_user_body_params
        params = await get_user_body_params(999997)
        assert params["name"] is None
        assert params["height_cm"] is None
        assert params["weight_kg"] is None
        assert params["language"] == "en"


class TestSaveOutfitCheck:
    async def test_saves_check(self, db_session):
        from sqlalchemy import select
        from app.db.database import get_or_create_user, save_outfit_check
        from app.db.models import OutfitCheck
        await get_or_create_user(800)
        with patch("app.storage.image_storage.delete_image"):
            await save_outfit_check(800, "/fake/path.jpg", "Style Score: 8/10")
        # Verify it was saved
        from app.db.database import async_session
        async with async_session() as session:
            result = await session.execute(select(OutfitCheck))
            checks = result.scalars().all()
        assert len(checks) == 1
        assert checks[0].image_path == "/fake/path.jpg"

    async def test_prunes_old_checks_beyond_max(self, db_session):
        from sqlalchemy import select
        from app.db.database import get_or_create_user, save_outfit_check
        from app.db.models import OutfitCheck
        from app.utils.config import settings
        await get_or_create_user(801)
        with patch("app.storage.image_storage.delete_image"):
            for i in range(settings.max_stored_checks + 2):
                await save_outfit_check(801, f"/fake/{i}.jpg", f"Result {i}")
        from app.db.database import async_session
        async with async_session() as session:
            from sqlalchemy import text
            result = await session.execute(
                select(OutfitCheck).order_by(OutfitCheck.created_at.desc())
            )
            checks = result.scalars().all()
        assert len(checks) <= settings.max_stored_checks
