from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import (
    criteria_keyboard,
    feedback_style_keyboard,
    language_keyboard,
    main_menu_keyboard,
    ALL_CRITERIA,
)
from app.bot.states import Onboarding
from app.db.database import (
    complete_onboarding,
    get_or_create_user,
    get_user_body_params,
    is_onboarding_complete,
    upsert_language,
)
from app.utils.i18n import t
from app.utils.logger import logger

router = Router()

_DEFAULT_CRITERIA = ",".join(ALL_CRITERIA)


def _parse_positive_int(text: str, min_val: int, max_val: int):
    try:
        val = int(text.strip())
        return val if min_val <= val <= max_val else None
    except ValueError:
        return None


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
        await message.answer(t("choose_language", "en"), reply_markup=language_keyboard())
        await state.set_state(Onboarding.waiting_for_name)


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
    await state.update_data(weight_kg=weight)
    # Move to criteria selection — default all selected
    selected = list(ALL_CRITERIA)
    await state.update_data(selected_criteria=selected)
    await state.set_state(Onboarding.waiting_for_criteria)
    await message.answer(t("ask_criteria", lang), reply_markup=criteria_keyboard(selected, lang))


@router.callback_query(Onboarding.waiting_for_criteria, F.data.startswith("criteria:"))
async def on_criteria_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    data = await state.get_data()
    lang = data.get("lang", "en")
    selected: list = list(data.get("selected_criteria", list(ALL_CRITERIA)))
    action = callback.data.split(":", 2)

    if action[1] == "toggle" and len(action) == 3:
        key = action[2]
        if key in selected:
            if len(selected) > 1:  # Must keep at least 1
                selected.remove(key)
        else:
            selected.append(key)
        await state.update_data(selected_criteria=selected)
        await callback.message.edit_reply_markup(reply_markup=criteria_keyboard(selected, lang))
        await callback.answer()

    elif action[1] == "done":
        await callback.answer()
        await state.update_data(selected_criteria=selected)
        await state.set_state(Onboarding.waiting_for_feedback_style)
        await callback.message.answer(
            t("ask_feedback_style", lang),
            reply_markup=feedback_style_keyboard(lang, current="friendly"),
        )


@router.callback_query(Onboarding.waiting_for_feedback_style, F.data.startswith("feedback_style:"))
async def on_feedback_style_selected(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    feedback_style = callback.data.split(":", 1)[1]
    data = await state.get_data()
    lang = data.get("lang", "en")
    name = data.get("name", "")
    height_cm = data.get("height_cm", 170)
    weight_kg = data.get("weight_kg", 70)
    selected_criteria = data.get("selected_criteria", list(ALL_CRITERIA))
    criteria_str = ",".join(selected_criteria)

    user_id = callback.from_user.id
    await complete_onboarding(user_id, name, height_cm, weight_kg, criteria_str, feedback_style)
    await state.clear()
    await callback.answer()
    await callback.message.answer(
        t("onboarding_complete", lang, name=name),
        reply_markup=main_menu_keyboard(lang),
    )
    logger.info(
        "Onboarding complete for user %s: %s %dcm %dkg criteria=%s feedback=%s",
        user_id, name, height_cm, weight_kg, criteria_str, feedback_style,
    )
