from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import occasion_back_keyboard, occasion_keyboard
from app.bot.states import OccasionSuggestions
from app.db.database import (
    get_user_access,
    get_user_body_params,
    get_user_language,
    is_onboarding_complete,
)
from app.services.gemini_service import QuotaExceededError
from app.services.outfit_analyzer import generate_occasion_suggestions
from app.utils.i18n import t
from app.utils.logger import logger

router = Router()

_OCCASION_BUTTONS = {"👔 Occasion Outfits", "👔 Ținute pentru Ocazii", "👔 Tinute pentru Ocazii", "👔 Образы для случая"}


@router.message(F.text.in_(_OCCASION_BUTTONS))
async def menu_occasion_outfits(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    if not await is_onboarding_complete(user_id):
        await message.answer(t("complete_profile_first", lang))
        return
    await state.clear()
    await state.set_state(OccasionSuggestions.waiting_for_occasion)
    await state.update_data(lang=lang)
    await message.answer(t("occasion_select_prompt", lang), reply_markup=occasion_keyboard(lang))


@router.callback_query(OccasionSuggestions.waiting_for_occasion, F.data.startswith("occasion:"))
async def on_occasion_selected(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    user_id = callback.from_user.id
    occasion = callback.data.split(":", 1)[1]
    data = await state.get_data()
    lang = data.get("lang", "en")

    _, api_key, _ = await get_user_access(user_id)

    await callback.answer()
    status_msg = await callback.message.answer(t("occasion_generating", lang))

    try:
        params = await get_user_body_params(user_id)
        result = await generate_occasion_suggestions(
            occasion=occasion,
            lang=lang,
            name=params.get("name"),
            height_cm=params.get("height_cm"),
            weight_kg=params.get("weight_kg"),
            api_key=api_key,
            style_criteria=params.get("style_criteria"),
            feedback_style=params.get("feedback_style", "friendly"),
        )

        await state.set_state(OccasionSuggestions.viewing_suggestions)
        await status_msg.edit_text(result, reply_markup=occasion_back_keyboard(lang))

    except QuotaExceededError:
        await status_msg.edit_text(t("quota_exceeded", lang))
    except Exception:
        logger.exception("Error generating occasion suggestions for user %s", user_id)
        await status_msg.edit_text(t("generic_error", lang))
