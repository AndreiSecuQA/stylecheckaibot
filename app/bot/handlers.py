import os
from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.bot.keyboards import main_menu_keyboard
from app.db.database import approve_user, get_all_users_summary, get_user_body_params, get_user_language
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


# ── Admin: approve / deny ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:approve:"))
async def on_admin_approve(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.from_user or not callback.message:
        return
    # Only admin can use this
    if callback.from_user.id != settings.admin_telegram_id:
        await callback.answer("⛔ Not authorized.", show_alert=True)
        return

    target_user_id = int(callback.data.split(":")[2])
    success = await approve_user(target_user_id)

    if success:
        await callback.answer(f"✅ User {target_user_id} approved.")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(f"✅ Approved user {target_user_id}.")
        # Notify the user
        try:
            lang = await get_user_language(target_user_id)
            await bot.send_message(target_user_id, t("approved_notification", lang))
        except Exception as e:
            logger.warning("Could not notify approved user %s: %s", target_user_id, e)
    else:
        await callback.answer(f"❌ User {target_user_id} not found.", show_alert=True)


@router.callback_query(F.data.startswith("admin:deny:"))
async def on_admin_deny(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.from_user or not callback.message:
        return
    if callback.from_user.id != settings.admin_telegram_id:
        await callback.answer("⛔ Not authorized.", show_alert=True)
        return

    target_user_id = int(callback.data.split(":")[2])
    await callback.answer(f"❌ User {target_user_id} denied.")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply(f"❌ Denied user {target_user_id}.")
    # Notify the user
    try:
        lang = await get_user_language(target_user_id)
        await bot.send_message(target_user_id, t("denied_notification", lang))
    except Exception as e:
        logger.warning("Could not notify denied user %s: %s", target_user_id, e)


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


# ── Admin: /resetuser command ─────────────────────────────────────────────────

@router.message(Command("resetuser"))
async def cmd_reset_user(message: Message) -> None:
    """Usage: /resetuser <user_id>  — resets free_uses_remaining to 5."""
    if not message.from_user or message.from_user.id != settings.admin_telegram_id:
        return
    parts = message.text.split() if message.text else []
    if len(parts) < 2:
        await message.answer("Usage: /resetuser <user_id>")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("Invalid user ID.")
        return
    from app.db.database import async_session
    from app.db.models import User
    from sqlalchemy import select
    async with async_session() as session:
        stmt = select(User).where(User.telegram_user_id == target_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            await message.answer(f"User {target_id} not found.")
            return
        user.free_uses_remaining = 5
        await session.commit()
    await message.answer(f"✅ Reset free uses to 5 for user {target_id}.")
    logger.info("Admin reset free uses for user %s", target_id)


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
    lines = [f"👥 Total users: {len(users)}\n"]
    for u in users[:20]:  # cap at 20 to avoid message too long
        status = "✅ approved" if u["is_approved"] else ("🔑 own key" if u["has_own_key"] else f"🆓 {u['free_uses_remaining']} left")
        lines.append(f"• {u['name']} (ID: {u['telegram_user_id']}) — {status} — {u['language']}")
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
