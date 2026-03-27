from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import access_keyboard, language_keyboard, main_menu_keyboard
from app.bot.states import Onboarding
from app.db.database import (
    complete_onboarding,
    get_or_create_user,
    get_user_body_params,
    is_onboarding_complete,
    set_gemini_api_key,
    approve_user,
    upsert_language,
)
from app.services.gemini_service import validate_user_api_key
from app.utils.config import settings
from app.utils.i18n import t
from app.utils.logger import logger

router = Router()


def _parse_positive_int(text: str, min_val: int, max_val: int):
    try:
        val = int(text.strip())
        return val if min_val <= val <= max_val else None
    except ValueError:
        return None


async def _notify_admin_approval_request(bot, user_id: int, name: str, lang: str) -> None:
    """Send approval request to admin with inline approve/deny buttons."""
    from app.bot.keyboards import admin_approval_keyboard
    admin_id = settings.admin_telegram_id
    if not admin_id:
        logger.warning("ADMIN_TELEGRAM_ID not set — approval request not sent")
        return
    try:
        text = (
            f"🔔 New access request:\n\n"
            f"User: {name}\n"
            f"ID: {user_id}\n"
            f"Language: {lang}"
        )
        await bot.send_message(admin_id, text, reply_markup=admin_approval_keyboard(user_id))
        logger.info("Approval request sent to admin for user %s", user_id)
    except Exception as e:
        logger.error("Failed to notify admin: %s", e)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    await get_or_create_user(user_id)
    done = await is_onboarding_complete(user_id)
    if done:
        await state.clear()
        params = await get_user_body_params(user_id)
        lang = params.get("language", "en")
        name = params.get("name") or ""
        await message.answer(
            t("welcome_back", lang, name=name) + "\n\n" + t("menu_title", lang),
            reply_markup=main_menu_keyboard(lang),
        )
    else:
        await state.clear()
        await message.answer(
            t("choose_language", "en"),
            reply_markup=language_keyboard(),
        )
        await state.set_state(Onboarding.waiting_for_name)


@router.message(Command("setkey"))
async def cmd_setkey(message: Message, state: FSMContext) -> None:
    """Allow existing users to update their Gemini API key."""
    if not message.from_user:
        return
    user_id = message.from_user.id
    lang = "en"
    params = await get_user_body_params(user_id)
    if params:
        lang = params.get("language", "en")
    await state.clear()
    await state.set_state(Onboarding.waiting_for_access)
    await state.update_data(lang=lang, setkey_mode=True)
    await message.answer(t("ask_gemini_key", lang))


@router.callback_query(F.data.startswith("lang:"))
async def on_language_selected(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not callback.from_user:
        return
    lang = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id
    await upsert_language(user_id, lang)
    await callback.answer()
    current_state = await state.get_state()
    if current_state == Onboarding.waiting_for_name:
        await state.update_data(lang=lang)
        if callback.message:
            await callback.message.answer(t("ask_name", lang))
    else:
        done = await is_onboarding_complete(user_id)
        if done:
            if callback.message:
                params = await get_user_body_params(user_id)
                name = params.get("name") or ""
                await callback.message.answer(
                    t("welcome_back", lang, name=name) + "\n\n" + t("menu_title", lang),
                    reply_markup=main_menu_keyboard(lang),
                )
        else:
            await state.set_state(Onboarding.waiting_for_name)
            await state.update_data(lang=lang)
            if callback.message:
                await callback.message.answer(t("ask_name", lang))


@router.message(Onboarding.waiting_for_name, F.text)
async def on_name_entered(message: Message, state: FSMContext) -> None:
    if not message.text or not message.from_user:
        return
    name = message.text.strip()
    if not name or name.startswith("/"):
        data = await state.get_data()
        lang = data.get("lang", "en")
        await message.answer(t("ask_name", lang))
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    await state.update_data(name=name)
    await state.set_state(Onboarding.waiting_for_height)
    await message.answer(t("ask_height", lang))


@router.message(Onboarding.waiting_for_height, F.text)
async def on_height_entered(message: Message, state: FSMContext) -> None:
    if not message.text or not message.from_user:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    height = _parse_positive_int(message.text, 100, 250)
    if height is None:
        await message.answer(t("height_range_error", lang))
        return
    await state.update_data(height_cm=height)
    await state.set_state(Onboarding.waiting_for_weight)
    await message.answer(t("ask_weight", lang))


@router.message(Onboarding.waiting_for_weight, F.text)
async def on_weight_entered(message: Message, state: FSMContext) -> None:
    if not message.text or not message.from_user:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    weight = _parse_positive_int(message.text, 30, 300)
    if weight is None:
        await message.answer(t("weight_range_error", lang))
        return
    name = data.get("name", "")
    height_cm = data.get("height_cm", 170)
    user_id = message.from_user.id
    await complete_onboarding(user_id, name, height_cm, weight)
    await state.update_data(weight_kg=weight)
    await state.set_state(Onboarding.waiting_for_access)
    await message.answer(t("ask_access", lang), reply_markup=access_keyboard(lang))
    logger.info("Onboarding body data complete for user %s: %s %dcm %dkg", user_id, name, height_cm, weight)


# ── Access step ────────────────────────────────────────────────────────────────

@router.callback_query(Onboarding.waiting_for_access, F.data == "access:own_key")
async def on_choose_own_key(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    await callback.answer()
    await state.update_data(awaiting_key_input=True)
    await callback.message.answer(t("ask_gemini_key", lang))


@router.callback_query(Onboarding.waiting_for_access, F.data == "access:request_approval")
async def on_choose_request_approval(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if not callback.from_user or not callback.message:
        return
    user_id = callback.from_user.id
    data = await state.get_data()
    lang = data.get("lang", "en")
    name = data.get("name", str(user_id))
    await callback.answer()
    await state.clear()
    # Notify admin
    await _notify_admin_approval_request(bot, user_id, name, lang)
    await callback.message.answer(
        t("approval_requested", lang),
        reply_markup=main_menu_keyboard(lang),
    )


@router.message(Onboarding.waiting_for_access, F.text)
async def on_gemini_key_entered(message: Message, state: FSMContext) -> None:
    """Handle the Gemini API key the user pastes."""
    if not message.text or not message.from_user:
        return
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data.get("lang", "en")
    api_key = message.text.strip()

    # Basic format check
    if not api_key.startswith("AIza") or len(api_key) < 20:
        await message.answer(t("key_invalid", lang))
        return

    status_msg = await message.answer(t("validating_key", lang))
    is_valid = await validate_user_api_key(api_key)

    if not is_valid:
        await status_msg.edit_text(t("key_invalid", lang))
        return

    await set_gemini_api_key(user_id, api_key)
    await state.clear()
    params = await get_user_body_params(user_id)
    name = params.get("name") or ""
    await status_msg.edit_text(t("key_valid", lang))
    await message.answer(
        t("onboarding_complete", lang, name=name),
        reply_markup=main_menu_keyboard(lang),
    )
    logger.info("User %s set their own Gemini API key", user_id)
