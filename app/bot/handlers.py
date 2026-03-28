import os
from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from app.bot.keyboards import main_menu_keyboard
from app.db.database import get_all_users_summary, get_user_body_params, get_user_language
from app.services.gemini_service import QuotaExceededError
from app.services.outfit_analyzer import answer_question
from app.utils.config import settings
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
    text = t("welcome_back", lang, name=name) + "\n\n" + t("menu_title", lang) if name else t("menu_title", lang)
    await callback.answer()
    await callback.message.answer(text, reply_markup=main_menu_keyboard(lang))


# ── Admin: /photos command ────────────────────────────────────────────────────

@router.message(Command("photos"))
async def cmd_photos(message: Message, bot: Bot) -> None:
    """Usage: /photos <user_id>  — sends all stored photos for a user."""
    if not message.from_user or message.from_user.id != settings.admin_telegram_id:
        return
    parts = message.text.split() if message.text else []
    if len(parts) < 2:
        # List all users who have photos
        images_dir = settings.images_dir
        if not images_dir.exists():
            await message.answer("📂 No images directory found.")
            return
        user_dirs = [d for d in images_dir.iterdir() if d.is_dir()]
        if not user_dirs:
            await message.answer("📂 No photos stored yet.")
            return
        lines = ["📂 Users with photos:\n"]
        for d in sorted(user_dirs):
            count = len(list(d.glob("*.jpg")))
            lines.append(f"• ID: {d.name} — {count} photo(s)  →  /photos {d.name}")
        await message.answer("\n".join(lines))
        return

    target_id = parts[1]
    user_dir = settings.images_dir / target_id
    if not user_dir.exists():
        await message.answer(f"📂 No photos found for user {target_id}.")
        return

    photos = sorted(user_dir.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not photos:
        await message.answer(f"📂 No photos found for user {target_id}.")
        return

    await message.answer(f"📸 Sending {len(photos)} photo(s) for user {target_id}...")
    for photo_path in photos[:10]:  # cap at 10 to avoid spam
        try:
            with open(photo_path, "rb") as f:
                photo_bytes = f.read()
            await bot.send_photo(
                message.chat.id,
                BufferedInputFile(photo_bytes, filename=photo_path.name),
                caption=f"🗂 {photo_path.name}",
            )
        except Exception as e:
            logger.error("Failed to send photo %s: %s", photo_path, e)
            await message.answer(f"⚠️ Could not send {photo_path.name}")


# ── Admin: /users command ──────────────────────────────────────────────────────

@router.message(Command("users"))
async def cmd_users(message: Message) -> None:
    if not message.from_user:
        return
    if message.from_user.id != settings.admin_telegram_id:
        return  # Silently ignore non-admin
    users = await get_all_users_summary()
    if not users:
        await message.answer("No users yet.")
        return
    complete = sum(1 for u in users if u["onboarding_complete"])
    lines = [f"👥 Total users: {len(users)} ({complete} onboarded)\n"]
    for u in users[:30]:  # cap at 30 to avoid message too long
        flag = "✅" if u["onboarding_complete"] else "⏳"
        lines.append(
            f"{flag} {u['name']} (ID: {u['telegram_user_id']}) — {u['language']}"
        )
    await message.answer("\n".join(lines))


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
