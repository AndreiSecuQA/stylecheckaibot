import datetime
import os
from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.bot.keyboards import (
    admin_unlock_keyboard,
    main_menu_keyboard,
    payment_confirm_keyboard,
    plan_selection_keyboard,
    upgrade_keyboard,
)
import asyncio

from app.db.database import (
    get_all_onboarded_users,
    get_all_users_summary,
    get_user_body_params,
    get_user_language,
    set_subscription,
)
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


# ── Payment: choose plan ─────────────────────────────────────────────────────

@router.callback_query(F.data == "payment:choose_plan")
async def on_choose_plan(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_language(callback.from_user.id)
    await callback.answer()
    await callback.message.answer(t("payment_choose_plan", lang), reply_markup=plan_selection_keyboard(lang))


@router.callback_query(F.data.startswith("payment:plan:"))
async def on_plan_selected(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    plan = callback.data.split(":")[-1]  # "monthly" or "lifetime"
    lang = await get_user_language(callback.from_user.id)
    await callback.answer()
    key = "payment_instructions_monthly" if plan == "monthly" else "payment_instructions_lifetime"
    await callback.message.answer(t(key, lang), reply_markup=payment_confirm_keyboard(lang, plan))


@router.callback_query(F.data.startswith("payment:confirm:"))
async def on_payment_confirm(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.from_user or not callback.message:
        return
    plan = callback.data.split(":")[-1]  # "monthly" or "lifetime"
    user_id = callback.from_user.id
    params = await get_user_body_params(user_id)
    lang = params.get("language", "en")
    name = params.get("name") or f"ID {user_id}"

    plan_label = "1 lună — 40 lei" if plan == "monthly" else "Toată viața — 500 lei"

    # Notify admin
    if settings.admin_telegram_id:
        admin_text = t("admin_payment_request", "ro",
                       name=name, user_id=str(user_id), plan=plan_label, lang=lang)
        try:
            await bot.send_message(
                settings.admin_telegram_id,
                admin_text,
                reply_markup=admin_unlock_keyboard(user_id),
            )
        except Exception:
            logger.exception("Failed to notify admin about payment request from user %s", user_id)

    await callback.answer()
    await callback.message.answer(t("payment_confirm_sent", lang))


# ── Admin: unlock / deny payment ─────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:unlock:"))
async def on_admin_unlock(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.from_user or not callback.message:
        return
    if callback.from_user.id != settings.admin_telegram_id:
        await callback.answer("Not authorized.", show_alert=True)
        return

    parts = callback.data.split(":")  # admin:unlock:monthly:USER_ID
    if len(parts) < 4:
        await callback.answer("Invalid callback data.")
        return

    sub_type = parts[2]   # "monthly" or "lifetime"
    target_user_id = int(parts[3])

    expires = None
    if sub_type == "monthly":
        expires = datetime.date.today() + datetime.timedelta(days=30)

    success = await set_subscription(target_user_id, sub_type, expires)
    if not success:
        await callback.answer("User not found in DB.", show_alert=True)
        return

    # Notify the user
    user_lang = await get_user_language(target_user_id)
    notification_key = "payment_confirmed_monthly" if sub_type == "monthly" else "payment_confirmed_lifetime"
    try:
        await bot.send_message(target_user_id, t(notification_key, user_lang),
                               reply_markup=main_menu_keyboard(user_lang))
    except Exception:
        logger.warning("Could not send unlock notification to user %s", target_user_id)

    # Edit admin message to confirm action
    label = "1 lună" if sub_type == "monthly" else "Lifetime"
    exp_str = f" (expiră {expires})" if expires else ""
    await callback.answer(f"✅ Deblocat {label}{exp_str}", show_alert=True)
    try:
        await callback.message.edit_text(
            callback.message.text + f"\n\n✅ Admin action: Deblocat {label}{exp_str}",
            reply_markup=None,
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin:deny_payment:"))
async def on_admin_deny_payment(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.from_user or not callback.message:
        return
    if callback.from_user.id != settings.admin_telegram_id:
        await callback.answer("Not authorized.", show_alert=True)
        return

    target_user_id = int(callback.data.split(":")[-1])
    user_lang = await get_user_language(target_user_id)

    try:
        await bot.send_message(target_user_id, t("payment_denied", user_lang))
    except Exception:
        logger.warning("Could not send denial notification to user %s", target_user_id)

    await callback.answer("❌ Refuzat", show_alert=True)
    try:
        await callback.message.edit_text(
            callback.message.text + "\n\n❌ Admin action: Refuzat",
            reply_markup=None,
        )
    except Exception:
        pass


# ── Admin: /broadcast command ────────────────────────────────────────────────

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot: Bot) -> None:
    """Send v2 update message to all onboarded users in their own language.
    Usage: /broadcast          — dry run (shows count only)
           /broadcast confirm  — actually sends
    """
    if not message.from_user or message.from_user.id != settings.admin_telegram_id:
        return

    parts = message.text.split() if message.text else []
    dry_run = len(parts) < 2 or parts[1].lower() != "confirm"

    users = await get_all_onboarded_users()
    if not users:
        await message.answer("No onboarded users found.")
        return

    if dry_run:
        await message.answer(
            f"📢 Ready to broadcast to {len(users)} onboarded users.\n\n"
            f"Send /broadcast confirm to actually send it."
        )
        return

    status = await message.answer(f"📢 Sending to {len(users)} users...")
    sent = 0
    failed = 0

    for user in users:
        try:
            uid = user["telegram_user_id"]
            lang = user["language"]
            name = user["name"]
            text = t("broadcast_v2", lang)
            if name:
                text = f"👋 {name}!\n\n" + text
            await bot.send_message(uid, text)
            sent += 1
            # Small delay to avoid hitting Telegram rate limits (30 msg/sec)
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.warning("Broadcast failed for user %s: %s", user["telegram_user_id"], e)
            failed += 1

    await status.edit_text(
        f"✅ Broadcast complete!\n\n"
        f"• Sent: {sent}\n"
        f"• Failed: {failed} (user blocked bot or never started it)"
    )


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
