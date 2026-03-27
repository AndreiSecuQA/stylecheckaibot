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
            InlineKeyboardButton(text="🇷🇴 Romana",  callback_data="lang:ro"),
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
            [InlineKeyboardButton(text=t("btn_get_perfect",   lang), callback_data="action:perfect_outfit")],
            [InlineKeyboardButton(text=t("btn_change_colors", lang), callback_data="action:change_colors")],
            [InlineKeyboardButton(text=t("btn_back_to_menu",  lang), callback_data="action:back_to_menu")],
        ]
    )


def occasion_photo_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_send_another",  lang), callback_data="action:send_another")],
            [InlineKeyboardButton(text=t("btn_back_to_menu",  lang), callback_data="action:back_to_menu")],
        ]
    )


def buy_result_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_analyze_another", lang), callback_data="action:analyze_another")],
            [InlineKeyboardButton(text=t("btn_back_to_menu",    lang), callback_data="action:back_to_menu")],
        ]
    )


# Legacy alias kept so old imports don't break during transition
def post_analysis_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return rate_outfit_keyboard(lang)
