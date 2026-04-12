import asyncio

from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import buy_feedback_keyboard, buy_rating_keyboard, upgrade_keyboard
from app.bot.states import BuySupport
from app.db.database import (
    check_weekly_limit,
    get_user_access,
    get_user_body_params,
    get_user_language,
    is_onboarding_complete,
)
from app.services.gemini_service import QuotaExceededError
from app.services.outfit_analyzer import (
    NotFashionImageError,
    analyze_buy_item_initial,
    analyze_buy_item_rating,
)
from app.storage.image_storage import save_image
from app.utils.config import settings
from app.utils.i18n import t
from app.utils.logger import logger
from app.utils.photo_cleanup import schedule_photo_deletion

router = Router()

_BUY_BUTTONS = {"🛍 Buy Support", "🛍 Sfaturi Cumpărături", "🛍 Sfaturi Cumparaturi", "🛍 Советы по покупке"}


@router.message(F.text.in_(_BUY_BUTTONS))
async def menu_buy_support(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    if not await is_onboarding_complete(user_id):
        await message.answer(t("complete_profile_first", lang))
        return
    await state.clear()
    await state.set_state(BuySupport.waiting_for_photo)
    await state.update_data(lang=lang)
    await message.answer(t("buy_send_photo", lang))


@router.message(BuySupport.waiting_for_photo, F.photo)
async def on_buy_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not message.photo:
        return
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data.get("lang", "en")

    # Check weekly limit
    if not await check_weekly_limit(user_id):
        await message.answer(t("weekly_limit_reached", lang), reply_markup=upgrade_keyboard(lang))
        return

    _, api_key, _ = await get_user_access(user_id)
    status_msg = await message.answer(t("buy_analyzing_initial", lang))
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
        asyncio.create_task(schedule_photo_deletion(bot, user_id, image_path, lang))

        params_body = await get_user_body_params(user_id)
        result = await analyze_buy_item_initial(
            image_path, lang, api_key=api_key,
            style_criteria=params_body.get("style_criteria"),
            feedback_style=params_body.get("feedback_style", "friendly"),
        )

        await state.update_data(image_path=image_path, api_key=api_key)
        await state.set_state(BuySupport.viewing_initial_feedback)
        await status_msg.edit_text(result, reply_markup=buy_feedback_keyboard(lang))

    except NotFashionImageError:
        await status_msg.edit_text(t("not_fashion_image", lang))
    except QuotaExceededError:
        await status_msg.edit_text(t("quota_exceeded", lang))
    except Exception:
        logger.exception("Error in buy support photo for user %s", user_id)
        await status_msg.edit_text(t("generic_error", lang))


@router.callback_query(BuySupport.viewing_initial_feedback, F.data == "buy:add_brand_price")
async def on_add_brand_price(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    await callback.answer()
    await state.set_state(BuySupport.waiting_for_brand_price)
    await callback.message.answer(t("buy_ask_price_brand", lang))


@router.message(BuySupport.waiting_for_brand_price, F.text)
async def on_brand_price_entered(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.text or not message.from_user:
        return
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data.get("lang", "en")
    image_path = data.get("image_path", "")
    api_key = data.get("api_key")
    price_brand = message.text.strip()

    status_msg = await message.answer(t("buy_analyzing_rating", lang))
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    params = await get_user_body_params(user_id)
    try:
        result = await analyze_buy_item_rating(
            image_path=image_path,
            price_brand=price_brand,
            lang=lang,
            name=params.get("name"),
            height_cm=params.get("height_cm"),
            weight_kg=params.get("weight_kg"),
            api_key=api_key,
            style_criteria=params.get("style_criteria"),
            feedback_style=params.get("feedback_style", "friendly"),
        )
        await state.set_state(BuySupport.viewing_rating)
        await status_msg.edit_text(result, reply_markup=buy_rating_keyboard(lang))

    except NotFashionImageError:
        await status_msg.edit_text(t("not_fashion_image", lang))
    except QuotaExceededError:
        await status_msg.edit_text(t("quota_exceeded", lang))
    except Exception:
        logger.exception("Error in buy rating for user %s", user_id)
        await status_msg.edit_text(t("generic_error", lang))


@router.callback_query(
    F.data == "action:analyze_another",
    F.func(lambda c: True),  # matches from both states
)
async def on_analyze_another(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    # Keep lang in state but reset other data
    await state.set_state(BuySupport.waiting_for_photo)
    await state.update_data(image_path=None, api_key=None)
    await callback.answer()
    await callback.message.answer(t("buy_send_photo", lang))
