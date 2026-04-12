from __future__ import annotations
from typing import List
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from app.utils.i18n import t

OCCASION_KEYS = ["casual", "work", "date", "sport", "event", "party", "beach", "wedding"]

ALL_CRITERIA = [
    "color_harmony", "body_proportions", "fit_silhouette", "occasion_fit",
    "fabric_texture", "trends", "accessories", "layering", "footwear", "personal_style",
]

FEEDBACK_STYLES = ["short", "friendly", "diplomatic", "detailed"]

ALL_FEEDBACK_SECTIONS = ["style_score", "colors", "fit", "proportions", "occasion", "quick_tip"]


def _chunk(lst: List, n: int) -> List[List]:
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🇬🇧 English",  callback_data="lang:en"),
            InlineKeyboardButton(text="🇷🇴 Română",   callback_data="lang:ro"),
            InlineKeyboardButton(text="🇷🇺 Русский",  callback_data="lang:ru"),
        ]]
    )


def main_menu_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_rate_outfit", lang))],
            [KeyboardButton(text=t("btn_occasion", lang))],
            [KeyboardButton(text=t("btn_buy_support", lang))],
            [KeyboardButton(text=t("btn_settings", lang))],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def criteria_keyboard(selected: List[str], lang: str = "en") -> InlineKeyboardMarkup:
    """Multiselect keyboard for style criteria. Shows checkmark for selected, square for not."""
    rows = []
    for i in range(0, len(ALL_CRITERIA), 2):
        row = []
        for key in ALL_CRITERIA[i:i+2]:
            label = t(f"criteria_{key}", lang)
            prefix = "✅ " if key in selected else "⬜ "
            row.append(InlineKeyboardButton(
                text=prefix + label,
                callback_data=f"criteria:toggle:{key}",
            ))
        rows.append(row)
    n = len(selected)
    rows.append([InlineKeyboardButton(
        text=t("btn_criteria_done", lang, n=str(n)),
        callback_data="criteria:done",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def feedback_style_keyboard(lang: str = "en", current: str = "") -> InlineKeyboardMarkup:
    """Single-select keyboard for feedback style."""
    rows = []
    for style in FEEDBACK_STYLES:
        label = t(f"feedback_{style}", lang)
        prefix = "✅ " if style == current else ""
        rows.append([InlineKeyboardButton(
            text=prefix + label,
            callback_data=f"feedback_style:{style}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def feedback_sections_keyboard(selected: List[str], lang: str = "en") -> InlineKeyboardMarkup:
    """Multiselect keyboard for outfit feedback sections."""
    rows = []
    for i in range(0, len(ALL_FEEDBACK_SECTIONS), 2):
        row = []
        for key in ALL_FEEDBACK_SECTIONS[i:i+2]:
            label = t(f"section_{key}", lang)
            prefix = "✅ " if key in selected else "⬜ "
            row.append(InlineKeyboardButton(
                text=prefix + label,
                callback_data=f"section:toggle:{key}",
            ))
        rows.append(row)
    n = len(selected)
    rows.append([InlineKeyboardButton(
        text=t("btn_criteria_done", lang, n=str(n)),
        callback_data="section:done",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def settings_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("settings_edit_language", lang),  callback_data="settings:language")],
            [InlineKeyboardButton(text=t("settings_edit_body", lang),      callback_data="settings:body")],
            [InlineKeyboardButton(text=t("settings_edit_criteria", lang),  callback_data="settings:criteria")],
            [InlineKeyboardButton(text=t("settings_edit_feedback", lang),  callback_data="settings:feedback")],
            [InlineKeyboardButton(text=t("settings_edit_sections", lang),  callback_data="settings:sections")],
            [InlineKeyboardButton(text=t("btn_back_to_menu", lang),        callback_data="action:back_to_menu")],
        ]
    )


def access_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_enter_own_key", lang),    callback_data="access:own_key")],
            [InlineKeyboardButton(text=t("btn_request_approval", lang), callback_data="access:request_approval")],
        ]
    )


def occasion_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=t(f"occasion_{key}", lang),
            callback_data=f"occasion:{t(f'occasion_{key}', 'en')}",
        )
        for key in OCCASION_KEYS
    ]
    rows = _chunk(buttons, 2)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def rate_outfit_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_tips_for_10", lang),   callback_data="action:tips_for_10")],
            [InlineKeyboardButton(text=t("btn_check_fabric", lang),  callback_data="action:check_fabric")],
            [InlineKeyboardButton(text=t("btn_back_to_menu", lang),  callback_data="action:back_to_menu")],
        ]
    )


def buy_feedback_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_add_brand_price", lang),  callback_data="buy:add_brand_price")],
            [InlineKeyboardButton(text=t("btn_analyze_another", lang),  callback_data="action:analyze_another")],
            [InlineKeyboardButton(text=t("btn_back_to_menu", lang),     callback_data="action:back_to_menu")],
        ]
    )


def buy_rating_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_analyze_another", lang), callback_data="action:analyze_another")],
            [InlineKeyboardButton(text=t("btn_back_to_menu", lang),    callback_data="action:back_to_menu")],
        ]
    )


def occasion_back_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="action:back_to_menu")],
        ]
    )


def admin_approval_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="✅ Approve", callback_data=f"admin:approve:{user_id}"),
            InlineKeyboardButton(text="❌ Deny",    callback_data=f"admin:deny:{user_id}"),
        ]]
    )


# ── Subscription / Payment keyboards ─────────────────────────────────────────

def upgrade_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Shown when a free user hits the weekly limit."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=t("btn_want_unlimited", lang), callback_data="payment:choose_plan"),
        ]]
    )


def plan_selection_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Plan picker: 1 month or lifetime."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_plan_monthly",  lang), callback_data="payment:plan:monthly")],
            [InlineKeyboardButton(text=t("btn_plan_lifetime", lang), callback_data="payment:plan:lifetime")],
        ]
    )


def payment_confirm_keyboard(lang: str = "en", plan: str = "monthly") -> InlineKeyboardMarkup:
    """Shown after payment instructions — confirm + back."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_request_payment_confirm", lang), callback_data=f"payment:confirm:{plan}")],
            [InlineKeyboardButton(text=t("btn_back_to_plans", lang),           callback_data="payment:choose_plan")],
        ]
    )


def admin_unlock_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Sent to admin when user requests payment confirmation."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ 1 lună",   callback_data=f"admin:unlock:monthly:{user_id}"),
                InlineKeyboardButton(text="✅ Lifetime", callback_data=f"admin:unlock:lifetime:{user_id}"),
            ],
            [InlineKeyboardButton(text="❌ Refuză",  callback_data=f"admin:deny_payment:{user_id}")],
        ]
    )


# Legacy aliases
def rate_outfit_keyboard_legacy(lang: str = "en") -> InlineKeyboardMarkup:
    return rate_outfit_keyboard(lang)

def post_analysis_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return rate_outfit_keyboard(lang)

def buy_result_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return buy_rating_keyboard(lang)

def occasion_photo_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return occasion_back_keyboard(lang)
