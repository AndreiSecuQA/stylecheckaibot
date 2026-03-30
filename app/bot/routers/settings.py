from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import (
    ALL_CRITERIA,
    ALL_FEEDBACK_SECTIONS,
    criteria_keyboard,
    feedback_sections_keyboard,
    feedback_style_keyboard,
    language_keyboard,
    main_menu_keyboard,
    settings_keyboard,
)
from app.bot.states import EditProfile
from app.db.database import get_user_body_params, get_user_language, update_user_preferences
from app.utils.i18n import t
from app.utils.logger import logger

router = Router()

_SETTINGS_BUTTONS = {
    "⚙️ My Profile", "⚙️ Profilul Meu", "⚙️ Мой профиль",
}

_FEEDBACK_LABELS = {
    "short": "⚡ Short",
    "friendly": "😊 Friendly",
    "diplomatic": "🤝 Diplomatic",
    "detailed": "📋 Detailed",
}


async def _show_settings(message_or_callback, user_id: int, lang: str) -> None:
    params = await get_user_body_params(user_id)
    name = params.get("name") or "—"
    height = params.get("height_cm") or "—"
    weight = params.get("weight_kg") or "—"
    criteria_str = params.get("style_criteria", "")
    criteria_count = len([c for c in criteria_str.split(",") if c.strip()]) if criteria_str else 10
    feedback = params.get("feedback_style", "friendly")
    feedback_label = _FEEDBACK_LABELS.get(feedback, feedback)
    lang_display = {"en": "🇬🇧 English", "ro": "🇷🇴 Română", "ru": "🇷🇺 Русский"}.get(lang, lang)

    text = t(
        "settings_summary", lang,
        name=name, height=str(height), weight=str(weight),
        language=lang_display,
        criteria_count=str(criteria_count),
        feedback_style=feedback_label,
    )
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(text, reply_markup=settings_keyboard(lang))
    else:
        await message_or_callback.message.answer(text, reply_markup=settings_keyboard(lang))


@router.message(F.text.in_(_SETTINGS_BUTTONS))
async def menu_settings(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    await state.clear()
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    await state.set_state(EditProfile.choosing_setting)
    await _show_settings(message, user_id, lang)


@router.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    await state.clear()
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    await state.set_state(EditProfile.choosing_setting)
    await _show_settings(message, user_id, lang)


@router.callback_query(EditProfile.choosing_setting, F.data == "settings:language")
async def on_edit_language(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_language(callback.from_user.id)
    await callback.answer()
    await callback.message.answer(t("choose_language", lang), reply_markup=language_keyboard())


@router.callback_query(EditProfile.choosing_setting, F.data == "settings:body")
async def on_edit_body(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_language(callback.from_user.id)
    await state.set_state(EditProfile.editing_height)
    await state.update_data(lang=lang)
    await callback.answer()
    await callback.message.answer(t("settings_ask_new_height", lang))


@router.message(EditProfile.editing_height, F.text)
async def on_edit_height(message: Message, state: FSMContext) -> None:
    if not message.text or not message.from_user:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    try:
        val = int(message.text.strip())
        if not (100 <= val <= 250):
            raise ValueError
    except ValueError:
        await message.answer(t("height_range_error", lang))
        return
    await state.update_data(height_cm=val)
    await state.set_state(EditProfile.editing_weight)
    await message.answer(t("settings_ask_new_weight", lang))


@router.message(EditProfile.editing_weight, F.text)
async def on_edit_weight(message: Message, state: FSMContext) -> None:
    if not message.text or not message.from_user:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    try:
        val = int(message.text.strip())
        if not (30 <= val <= 300):
            raise ValueError
    except ValueError:
        await message.answer(t("weight_range_error", lang))
        return
    height_cm = data.get("height_cm")
    user_id = message.from_user.id
    await update_user_preferences(user_id, height_cm=height_cm, weight_kg=val)
    await state.set_state(EditProfile.choosing_setting)
    await message.answer(t("settings_saved", lang))
    await _show_settings(message, user_id, lang)


@router.callback_query(EditProfile.choosing_setting, F.data == "settings:criteria")
async def on_edit_criteria(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    params = await get_user_body_params(user_id)
    criteria_str = params.get("style_criteria", ",".join(ALL_CRITERIA))
    selected = [c.strip() for c in criteria_str.split(",") if c.strip()]
    await state.set_state(EditProfile.editing_criteria)
    await state.update_data(lang=lang, selected_criteria=selected)
    await callback.answer()
    await callback.message.answer(t("ask_criteria", lang), reply_markup=criteria_keyboard(selected, lang))


@router.callback_query(EditProfile.editing_criteria, F.data.startswith("criteria:"))
async def on_edit_criteria_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    selected: list = list(data.get("selected_criteria", list(ALL_CRITERIA)))
    parts = callback.data.split(":", 2)

    if parts[1] == "toggle" and len(parts) == 3:
        key = parts[2]
        if key in selected:
            if len(selected) > 1:
                selected.remove(key)
        else:
            selected.append(key)
        await state.update_data(selected_criteria=selected)
        await callback.message.edit_reply_markup(reply_markup=criteria_keyboard(selected, lang))
        await callback.answer()
    elif parts[1] == "done":
        user_id = callback.from_user.id
        criteria_str = ",".join(selected)
        await update_user_preferences(user_id, style_criteria=criteria_str)
        await state.set_state(EditProfile.choosing_setting)
        await callback.answer()
        await callback.message.answer(t("settings_saved", lang))
        await _show_settings(callback, user_id, lang)


@router.callback_query(EditProfile.choosing_setting, F.data == "settings:feedback")
async def on_edit_feedback(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    params = await get_user_body_params(user_id)
    current = params.get("feedback_style", "friendly")
    await state.set_state(EditProfile.editing_feedback_style)
    await state.update_data(lang=lang)
    await callback.answer()
    await callback.message.answer(t("ask_feedback_style", lang), reply_markup=feedback_style_keyboard(lang, current))


@router.callback_query(EditProfile.editing_feedback_style, F.data.startswith("feedback_style:"))
async def on_edit_feedback_selected(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    feedback_style = callback.data.split(":", 1)[1]
    data = await state.get_data()
    lang = data.get("lang", "en")
    user_id = callback.from_user.id
    await update_user_preferences(user_id, feedback_style=feedback_style)
    await state.set_state(EditProfile.choosing_setting)
    await callback.answer()
    await callback.message.answer(t("settings_saved", lang))
    await _show_settings(callback, user_id, lang)


@router.callback_query(EditProfile.choosing_setting, F.data == "settings:sections")
async def on_edit_sections(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    params = await get_user_body_params(user_id)
    sections_str = params.get("feedback_sections", ",".join(ALL_FEEDBACK_SECTIONS))
    selected = [s.strip() for s in sections_str.split(",") if s.strip()]
    await state.set_state(EditProfile.editing_feedback_sections)
    await state.update_data(lang=lang, selected_sections=selected)
    await callback.answer()
    await callback.message.answer(
        t("ask_feedback_sections", lang),
        reply_markup=feedback_sections_keyboard(selected, lang),
    )


@router.callback_query(EditProfile.editing_feedback_sections, F.data.startswith("section:"))
async def on_edit_sections_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    selected: list = list(data.get("selected_sections", list(ALL_FEEDBACK_SECTIONS)))
    parts = callback.data.split(":", 2)

    if parts[1] == "toggle" and len(parts) == 3:
        key = parts[2]
        if key in selected:
            if len(selected) > 1:  # keep at least 1
                selected.remove(key)
        else:
            selected.append(key)
        await state.update_data(selected_sections=selected)
        await callback.message.edit_reply_markup(
            reply_markup=feedback_sections_keyboard(selected, lang)
        )
        await callback.answer()

    elif parts[1] == "done":
        user_id = callback.from_user.id
        sections_str = ",".join(selected)
        await update_user_preferences(user_id, feedback_sections=sections_str)
        await state.set_state(EditProfile.choosing_setting)
        await callback.answer()
        await callback.message.answer(t("settings_saved", lang))
        await _show_settings(callback, user_id, lang)
