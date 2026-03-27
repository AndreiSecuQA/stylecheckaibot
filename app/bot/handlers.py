from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import main_menu_keyboard
from app.db.database import get_user_body_params, get_user_language
from app.services.gemini_service import QuotaExceededError
from app.services.outfit_analyzer import answer_question
from app.utils.i18n import t
from app.utils.logger import logger

router = Router()


# ── Back to menu (global — used by all flows) ─────────────────────────────────

@router.callback_query(F.data == "action:back_to_menu")
async def on_back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    await state.clear()
    user_id = callback.from_user.id
    params = await get_user_body_params(user_id)
    lang = params.get("language", "en")
    name = params.get("name") or ""
    text = t("welcome_back", lang, name=name) if name else t("menu_title", lang)
    await callback.answer()
    await callback.message.answer(text, reply_markup=main_menu_keyboard(lang))


# ── Document handler ──────────────────────────────────────────────────────────

@router.message(F.document)
async def on_document(message: Message) -> None:
    lang = "en"
    if message.from_user:
        lang = await get_user_language(message.from_user.id)
    await message.answer(t("not_photo", lang))


# ── Text catch-all (fashion Q&A) ──────────────────────────────────────────────

@router.message(F.text)
async def on_text(message: Message, bot: Bot) -> None:
    if not message.text or not message.from_user:
        return
    lang = await get_user_language(message.from_user.id)
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    try:
        answer = await answer_question(message.text, lang)
        await message.answer(answer)
    except QuotaExceededError:
        await message.answer(t("quota_exceeded", lang))
    except Exception:
        logger.exception("Error answering text question for user %s", message.from_user.id)
        await message.answer(t("generic_error", lang))


# ── Unknown message catch-all ─────────────────────────────────────────────────

@router.message()
async def on_unknown(message: Message) -> None:
    lang = "en"
    if message.from_user:
        lang = await get_user_language(message.from_user.id)
    await message.answer(t("unknown", lang))
