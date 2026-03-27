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


def _chunk(lst: List, n: int) -> List[List]:
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton(text="🇷🇴 Română",  callback_data="lang:ro"),
        ]]
    )


def main_menu_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_rate_outfit", lang))],
            [KeyboardButton(text=t("btn_occasion", lang))],
            [KeyboardButton(text=t("btn_buy_support", lang))],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def access_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Shown during onboarding — user chooses how to get access."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_enter_own_key", lang), callback_data="access:own_key")],
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
            [InlineKeyboardButton(text=t("btn_tips_for_10", lang), callback_data="action:tips_for_10")],
            [InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="action:back_to_menu")],
        ]
    )


def buy_feedback_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Shown after initial buy photo analysis — optional brand/price step."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_add_brand_price", lang), callback_data="buy:add_brand_price")],
            [InlineKeyboardButton(text=t("btn_analyze_another", lang), callback_data="action:analyze_another")],
            [InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="action:back_to_menu")],
        ]
    )


def buy_rating_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Shown after star rating — user can add another item."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_analyze_another", lang), callback_data="action:analyze_another")],
            [InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="action:back_to_menu")],
        ]
    )


def occasion_back_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="action:back_to_menu")],
        ]
    )


def admin_approval_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard sent to admin for approve/deny."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Approve", callback_data=f"admin:approve:{user_id}"),
                InlineKeyboardButton(text="❌ Deny",    callback_data=f"admin:deny:{user_id}"),
            ]
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
