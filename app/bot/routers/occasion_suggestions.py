from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import occasion_keyboard, occasion_photo_keyboard
from app.bot.states import OccasionSuggestions
from app.db.database import get_user_body_params, get_user_language, is_onboarding_complete
from app.services.gemini_service import QuotaExceededError
from app.services.outfit_analyzer import (
    NotFashionImageError,
    analyze_item_for_occasion,
    generate_occasion_outfit_ideas,
)
from app.storage.image_storage import save_image
from app.utils.config import settings
from app.utils.i18n import t
from app.utils.logger import logger

router = Router()

_OCCASION_BUTTONS = {"👔 Occasion Outfits", "👔 Tinute pentru Ocazii"}


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
    if not callback.data or not callback.from_user:
        return
    occasion = callback.data.split(":", 1)[1]
    data = await state.get_data()
    lang = data.get("lang", "en")
    await state.update_data(occasion=occasion)
    await state.set_state(OccasionSuggestions.waiting_for_budget)
    await callback.answer()
    if callback.message:
        await callback.message.answer(t("occasion_ask_budget", lang))


@router.message(OccasionSuggestions.waiting_for_budget, F.text)
async def on_budget_entered(message: Message, state: FSMContext) -> None:
    if not message.text or not message.from_user:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    await state.update_data(budget=message.text.strip())
    await state.set_state(OccasionSuggestions.waiting_for_style_vibe)
    await message.answer(t("occasion_ask_style_vibe", lang))


@router.message(OccasionSuggestions.waiting_for_style_vibe, F.text)
async def on_style_vibe_entered(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.text or not message.from_user:
        return
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data.get("lang", "en")
    occasion = data.get("occasion", "")
    budget = data.get("budget", "any")
    style_vibe = message.text.strip()
    await state.update_data(style_vibe=style_vibe)

    status_msg = await message.answer(t("occasion_generating", lang))
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    params = await get_user_body_params(user_id)
    try:
        result = await generate_occasion_outfit_ideas(
            occasion=occasion,
            budget=budget,
            style_vibe=style_vibe,
            lang=lang,
            name=params.get("name"),
            height_cm=params.get("height_cm"),
            weight_kg=params.get("weight_kg"),
        )
        await state.set_state(OccasionSuggestions.viewing_suggestions)
        await status_msg.edit_text(result)
        await message.answer(
            t("occasion_photo_invite", lang, occasion=occasion),
            reply_markup=occasion_photo_keyboard(lang),
        )
    except QuotaExceededError:
        await status_msg.edit_text(t("quota_exceeded", lang))
    except Exception:
        logger.exception("Error generating occasion outfit ideas for user %s", user_id)
        await status_msg.edit_text(t("generic_error", lang))


@router.message(OccasionSuggestions.viewing_suggestions, F.photo)
async def on_occasion_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not message.photo:
        return
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data.get("lang", "en")
    occasion = data.get("occasion", "")

    status_msg = await message.answer(t("occasion_photo_analyzing", lang, occasion=occasion))
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
        result = await analyze_item_for_occasion(image_path, occasion, lang)
        await status_msg.edit_text(result, reply_markup=occasion_photo_keyboard(lang))

    except NotFashionImageError:
        await status_msg.edit_text(t("not_fashion_image", lang))
    except QuotaExceededError:
        await status_msg.edit_text(t("quota_exceeded", lang))
    except Exception:
        logger.exception("Error analyzing occasion photo for user %s", user_id)
        await status_msg.edit_text(t("generic_error", lang))


@router.callback_query(OccasionSuggestions.viewing_suggestions, F.data == "action:send_another")
async def on_send_another(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    occasion = data.get("occasion", "")
    await callback.answer()
    await callback.message.answer(
        t("occasion_photo_invite", lang, occasion=occasion),
        reply_markup=occasion_photo_keyboard(lang),
    )
