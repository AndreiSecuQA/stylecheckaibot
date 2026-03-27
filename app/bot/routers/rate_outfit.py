from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import rate_outfit_keyboard
from app.bot.states import RateOutfit
from app.db.database import (
    check_daily_limit,
    decrement_free_uses,
    get_user_access,
    get_user_body_params,
    get_user_language,
    is_onboarding_complete,
    save_outfit_check,
)
from app.services.gemini_service import QuotaExceededError
from app.services.outfit_analyzer import (
    NotFashionImageError,
    analyze_outfit,
    generate_tips_for_10,
)
from app.storage.image_storage import save_image
from app.utils.config import settings
from app.utils.i18n import t
from app.utils.logger import logger

router = Router()

_RATE_BUTTONS = {"📸 Rate My Outfit", "📸 Evaluează Ținuta", "📸 Evalueaza Tinuta"}


@router.message(F.text.in_(_RATE_BUTTONS))
async def menu_rate_outfit(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    if not await is_onboarding_complete(user_id):
        await message.answer(t("complete_profile_first", lang))
        return
    await state.clear()
    await state.set_state(RateOutfit.waiting_for_photo)
    await message.answer(t("rate_send_photo", lang))


@router.message(RateOutfit.waiting_for_photo, F.photo)
async def on_rate_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not message.photo:
        return
    user_id = message.from_user.id
    lang = await get_user_language(user_id)

    # Check access
    has_access, api_key, free_remaining = await get_user_access(user_id)
    if not has_access:
        await message.answer(t("no_access", lang))
        return

    if not await check_daily_limit(user_id):
        await message.answer(t("daily_limit", lang))
        return

    status_msg = await message.answer(t("rate_analyzing", lang))
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)

    try:
        photo = message.photo[-1]
        if photo.file_size and photo.file_size > settings.max_image_size_bytes:
            await status_msg.edit_text(t("too_large", lang))
            return

        file = await bot.get_file(photo.file_id)
        if not file.file_path:
            await status_msg.edit_text(t("download_fail", lang))
            return

        file_bytes = await bot.download_file(file.file_path)
        if file_bytes is None:
            await status_msg.edit_text(t("download_fail", lang))
            return

        image_bytes = file_bytes.read()
        image_path = await save_image(user_id, image_bytes)
        params = await get_user_body_params(user_id)

        result = await analyze_outfit(
            image_path,
            occasion=None,
            lang=lang,
            name=params.get("name"),
            height_cm=params.get("height_cm"),
            weight_kg=params.get("weight_kg"),
            api_key=api_key,
        )

        # Decrement free uses if applicable
        if free_remaining > 0:
            remaining = await decrement_free_uses(user_id)
            if remaining > 0:
                analyses_word = "analysis" if remaining == 1 else "analyses"
                result += f"\n\n{t('free_uses_remaining', lang, count=str(remaining), analyses=analyses_word)}"

        await save_outfit_check(user_id, image_path, result)
        await state.update_data(last_image_path=image_path)
        await state.set_state(RateOutfit.viewing_results)
        await status_msg.edit_text(result, reply_markup=rate_outfit_keyboard(lang))

    except NotFashionImageError:
        await status_msg.edit_text(t("not_fashion_image", lang))
        await state.set_state(RateOutfit.waiting_for_photo)
    except QuotaExceededError:
        await status_msg.edit_text(t("quota_exceeded", lang))
    except Exception:
        logger.exception("Error processing rate outfit photo for user %s", user_id)
        await status_msg.edit_text(t("generic_error", lang))


@router.callback_query(RateOutfit.viewing_results, F.data == "action:tips_for_10")
async def on_tips_for_10(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if not callback.from_user or not callback.message:
        return
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    data = await state.get_data()
    image_path = data.get("last_image_path")
    if not image_path:
        await callback.answer()
        await callback.message.answer(t("send_photo_first", lang))
        return

    has_access, api_key, _ = await get_user_access(user_id)
    if not has_access:
        await callback.answer()
        await callback.message.answer(t("no_access", lang))
        return

    await callback.answer()
    status_msg = await callback.message.answer(t("generating_tips", lang))
    await bot.send_chat_action(chat_id=callback.message.chat.id, action=ChatAction.TYPING)

    try:
        params = await get_user_body_params(user_id)
        result = await generate_tips_for_10(
            image_path,
            lang,
            name=params.get("name"),
            height_cm=params.get("height_cm"),
            weight_kg=params.get("weight_kg"),
            api_key=api_key,
        )
        await status_msg.edit_text(result, reply_markup=rate_outfit_keyboard(lang))
    except NotFashionImageError:
        await status_msg.edit_text(t("not_fashion_image", lang))
    except QuotaExceededError:
        await status_msg.edit_text(t("quota_exceeded", lang))
    except Exception:
        logger.exception("Error generating tips for user %s", user_id)
        await status_msg.edit_text(t("generic_error", lang))


# ── Legacy callbacks (from old keyboard versions) ─────────────────────────────

@router.callback_query(RateOutfit.viewing_results, F.data == "action:perfect_outfit")
async def on_perfect_outfit_legacy(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await on_tips_for_10(callback, state, bot)


@router.callback_query(RateOutfit.viewing_results, F.data == "action:change_colors")
async def on_change_colors_legacy(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await on_tips_for_10(callback, state, bot)
